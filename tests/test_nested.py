import pytest
from pytest import CaptureFixture
from syrupy.assertion import SnapshotAssertion

from pydantic import Field
from pydantic_argparse_extensible import ArgModel


class CommonArgs(ArgModel):
    host: str = Field(description="""The host to connect to.""")


class Args(ArgModel):
    user: str = Field(description="""The username to connect to.""")

    common: CommonArgs


def test_required(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(args=["--help"])
    assert capsys.readouterr().out == snapshot


def test_parse() -> None:
    args = Args.argparse(args=["--user", "puppy", "--host", "doggy"])
    assert args == Args(user="puppy", common=CommonArgs(host="doggy"))
