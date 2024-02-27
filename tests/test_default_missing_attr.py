import argparse
from argparse import _ActionsContainer

from pydantic import Field

from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    account_ids: list[str] = Field(default_factory=lambda: ["1", "2", "3"])

    @classmethod
    def update_argparser(
        cls, parser: "_ActionsContainer", manual: set[str] | None = None
    ) -> None:
        parser.add_argument(
            "--account-id",
            action="append",
            dest="account_ids",
            default=argparse.SUPPRESS,
        )
        if manual is None:
            manual = set()
        manual.add("account_ids")
        return super().update_argparser(parser, manual)


def test_parse() -> None:
    args = Args.argparse(args=[])
    assert args == Args(account_ids=["1", "2", "3"])

    args = Args.argparse(args=["--account-id", "9999"])
    assert args == Args(account_ids=["9999"])

    args = Args.argparse(args=["--account-id", "9999", "--account-id", "413"])
    assert args == Args(account_ids=["9999", "413"])
