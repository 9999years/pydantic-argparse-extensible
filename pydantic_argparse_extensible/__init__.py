"""
A typed wrapper for `argparse` leveraging `pydantic` to generate command line
interfaces.
"""

from argparse import ArgumentParser, Namespace, _ActionsContainer
from typing import Any, Callable, Self, Sequence, get_origin, get_args, Union
from types import UnionType, NoneType

from pydantic import BaseModel
from pydantic_core import PydanticUndefined


class ArgModel(BaseModel):
    """
    Typed wrapper around an `ArgumentParser`.
    """

    @classmethod
    def field_name_to_argument_name(cls, field_name: str) -> str:
        """
        Convert a field name to an argument name.

        This is used as the first argument in the corresponding
        `ArgumentParser.add_argument` call.
        """

        return "--" + field_name.replace("_", "-")

    @classmethod
    def annotation_to_argument_type(
        cls, field_name: str, annotation: Any
    ) -> Callable[[], Any] | None:
        """
        Convert a field type annotation to an argument type function.

        The return value (if not `None`) is used as the `type=` argument in the
        corresponding `ArgumentParser.parse_argument` call.
        """
        # pylint: disable-next=consider-using-in
        if annotation == str or annotation == (str | None):
            return None
        elif (optional := _get_optional_type(annotation)) is not None:
            return optional
        elif callable(annotation):
            return annotation  # type: ignore
        else:
            message = f"Annotation is not callable: {annotation} on field {cls.__name__}.{field_name}"
            raise TypeError(message)

    @classmethod
    def update_argparser(
        cls, parser: _ActionsContainer, manual: set[str] | None = None
    ) -> None:
        """
        Add arguments corresponding to this class's fields to the given
        `parser`.

        The default implementation calls this method on all fields that also
        derive from `ArgModel`.

        Fields with names in `manual` will be ignored.
        """
        if manual is None:
            manual = set()

        for name, field in cls.model_fields.items():
            if name in manual:
                continue

            if field.annotation is None:  # pragma: no cover
                # I'm pretty sure this is unreachable, but the type annotations say otherwise.
                raise TypeError(f"Field {cls.__name__}.{name} has no annotation")

            if (
                # Note: The annotation can be a union like `str | None` which is not a class.
                isinstance(field.annotation, type)
                and issubclass(field.annotation, ArgModel)
            ):
                field.annotation.update_argparser(parser)
            else:
                kwargs: dict[str, Any] = {"dest": name}

                if (
                    field.default is not PydanticUndefined
                    or field.default_factory is not None
                ):
                    kwargs["default"] = field.get_default(call_default_factory=True)
                else:
                    kwargs["required"] = True

                arg_type = cls.annotation_to_argument_type(
                    field_name=name, annotation=field.annotation
                )
                if arg_type is not None:
                    if arg_type == bool:
                        kwargs["action"] = "store_true"
                        kwargs["required"] = False
                    else:
                        kwargs["type"] = arg_type

                if field.description is not None:
                    kwargs["help"] = field.description

                parser.add_argument(cls.field_name_to_argument_name(name), **kwargs)

    @classmethod
    def from_parsed_args(
        cls, args: Namespace, partial: dict[str, Any] | None = None
    ) -> Self:
        """
        Given arguments parsed from an `ArgumentParser` augmented with this
        class's `update_argparser` method, construct an instance of this class.

        The default implementation fills each field with the corresponding value in `args`.
        If the field derives from `ArgModel`, that field's `from_parsed_args`
        implementation is used.

        If `partial` is given, it's treated as a partially-filled set of
        arguments. Fields with values matching keys in `partial` will be
        ignored.
        """
        if partial is None:
            partial = {}
        ret = {}
        for name, field in cls.model_fields.items():
            if name in partial:
                ret[name] = partial[name]
            elif field.annotation is None:  # pragma: no cover
                # I'm pretty sure this is unreachable, but the type annotations say otherwise.
                raise TypeError(f"Field {cls.__name__}.{name} has no annotation")
            elif isinstance(field.annotation, type) and issubclass(
                field.annotation, ArgModel
            ):
                ret[name] = field.annotation.from_parsed_args(args)
            elif hasattr(args, name):
                ret[name] = getattr(args, name)
        return cls.model_validate(ret)

    @classmethod
    def argparse(  # pylint: disable=too-many-arguments
        cls,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
        parser: ArgumentParser | None = None,
        args: Sequence[str] | None = None,
    ) -> Self:
        """
        Create an `ArgumentParser` and parse the arguments into an instance of
        this class.
        """
        if parser is None:
            parser = ArgumentParser(
                prog=prog, usage=usage, description=description, epilog=epilog
            )
        cls.update_argparser(parser)
        parsed_args = parser.parse_args(args=args)
        return cls.from_parsed_args(parsed_args)


def _get_optional_type(annotation: Any) -> type | None:
    """For a given type annotation, if the annotation is of the form `T |
    None`, return `T`.

    For non-union annotations, or unions of more than two types, return `None`.
    """
    origin = get_origin(annotation)
    if origin is not Union and origin is not UnionType:
        return None

    args = get_args(annotation)
    if len(args) != 2:
        return None

    if args[0] is NoneType:
        return args[1]  # type: ignore
    else:
        return args[0]  # type: ignore
