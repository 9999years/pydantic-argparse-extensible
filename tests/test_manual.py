from argparse import _ActionsContainer, Namespace
from typing import Any, Self

import pytest
from pytest import CaptureFixture
from syrupy.assertion import SnapshotAssertion

from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    user: str

    @classmethod
    def update_argparser(
        cls, parser: _ActionsContainer, manual: set[str] | None = None
    ) -> None:
        if manual is None:
            manual = set()

        parser.add_argument("--my-user-flag", help="Put the username here :)")

        manual.add("user")
        return super().update_argparser(parser, manual)

    @classmethod
    def from_parsed_args(
        cls, args: Namespace, partial: dict[str, Any] | None = None
    ) -> Self:
        if partial is None:
            partial = {}

        partial["user"] = args.my_user_flag

        return super().from_parsed_args(args, partial)


def test_help(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(args=["--help"])
    assert capsys.readouterr().out == snapshot


def test_parse() -> None:
    args = Args.argparse(args=["--my-user-flag", "puppy"])
    assert args == Args(user="puppy")
