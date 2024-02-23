from pathlib import Path

import pytest
from pydantic_argparse_extensible import ArgModel
from pytest import CaptureFixture
from syrupy.assertion import SnapshotAssertion


class Args(ArgModel):
    infile: Path | None = None


def test_help(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(args=["--help"])
    assert capsys.readouterr().out == snapshot


def test_parse() -> None:
    args = Args.argparse(args=[])
    assert args == Args(infile=None)

    args = Args.argparse(args=["--infile", "puppy"])
    assert args == Args(infile=Path("puppy"))
