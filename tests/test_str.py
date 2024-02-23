from argparse import ArgumentParser
import pytest
from pytest import CaptureFixture
from syrupy.assertion import SnapshotAssertion

from pydantic import Field
from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    user: str = Field(description="""The username to connect to.""")

    host: str = Field(description="""The host to connect to.""")


def test_required(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(args=[])
    assert capsys.readouterr().err == snapshot


def test_default_argparser(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(parser=ArgumentParser(prog="puppy"), args=[])
    assert capsys.readouterr().err == snapshot


def test_parse() -> None:
    args = Args.argparse(args=["--user", "puppy", "--host", "doggy"])
    assert args == Args(user="puppy", host="doggy")
