# pydantic-argparse-extensible

A typed wrapper for [`argparse`][argparse] leveraging [`pydantic`][pydantic] to
generate command line interfaces.

The `pydantic_argparse_extensible` provides an `ArgModel` class, which inherits
from `pydantic.BaseModel` and provides a few new methods. For simple arguments,
there's not much you need to do:

```python
from pydantic import ConfigDict
from pydantic_argparse_extensible import ArgModel

class Args(ArgModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    user: str
    """The username to connect to."""

    host: str
    """The host to connect to."""

def main() -> None:
    args = Args.argparse()
    print(args)


if __name__ == "__main__":
    main()


# $ python -m example_simple --help
# usage: example_simple.py [-h] --user USER --host HOST
# 
# options:
#   -h, --help   show this help message and exit
#   --user USER  The username to connect to.
#   --host HOST  The host to connect to.
```

Then, `pydantic` helps ensure that all the data from `argparse` is typed as you
expect. Plus, we get autocompletion for argument fields on the `Args` class, as
well as hover documentation that matches the CLI `--help` output.

You can use `ArgModel`s as reusable sets of arguments. Here, `Args` will
include arguments defined on both of the models it includes:

```python
class CommonArgs(ArgModel):
    pass

class GitHubArgs(ArgModel):
    pass

class Args(ArgModel):
    common: CommonArgs
    github: GitHubArgs
```

The power of `pydantic_argparse_extensible` lies in letting you opt out of its
automatic generation logic in order to manually create more complex
command-line interfaces that aren't supported by `typer` and other
alternatives:

```python
class Address(BaseModel):
    user: str
    host: str

class Ec2Instance(BaseModel):
    address: Address
    instance_id: str

class Args(ArgModel):
    deploy: bool
    system_profile: Path = Path("/nix/var/nix/profiles/system")
    aws_role_arn: str | None = None
    ec2_instances: list[Ec2Instance]

    @classmethod
    def update_argparser(cls, parser: ArgumentParser, manual: set[str] | None = None) -> None:
        parser.add_argument(
            "--no-deploy",
            action="store_false",
            dest="deploy",
            help="Don't deploy the resulting builds.",
        )

        # This argument doesn't appear as a field at all, but it's used to help
        # define the `ec2_instances` field.
        parser.add_argument(
            "--ssh-user",
            help="Username to use when connecting to `--ec2-instance` hosts via SSH.",
        )

        parser.add_argument(
            "--ec2-instance",
            nargs=2,
            metavar=("HOST_NAME", "INSTANCE_ID"),
            dest="ec2_instances",
            help="AWS EC2 instances to deploy to, if any.",
        )

        # We defined arguments for the `deploy` and `ec2_instances` fields
        # manually, so we tell `pydantic_argparse_extensible` to skip them when
        # generating the CLI.
        super().update_argparser(parser, manual={"deploy", "ec2_instances"})

    @classmethod
    def from_parsed_args(cls, args: Namespace, partial: dict[str, Any] | None = None) -> Self:
        ec2_instances = []
        ssh_user = args.ssh_user
        if args.ec2_instances:
            ec2_instances = [
                Ec2Instance(address=Address(user=ssh_user, host=host), instance_id=instance_id)
                for (host, instance_id) in args.ec2_instances
            ]

        # We parsed the value for the `ec2_instances` field manually, so we
        # tell `pydantic_argparse_extensible` to ignore the `ec2_instances`
        # attribute on the `args` when constructing the model.
        partial = {"ec2_instances": ec2_instances}
        return super().from_parsed_args(args, partial)
```

[argparse]: https://docs.python.org/3/library/argparse.html
[pydantic]: https://docs.pydantic.dev/latest/
