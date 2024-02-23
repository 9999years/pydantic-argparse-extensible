from pathlib import Path

import pytest
from pydantic_argparse_extensible import ArgModel
from pytest import CaptureFixture
from syrupy.assertion import SnapshotAssertion


class Args(ArgModel):
    infile: Path | None = None


class Args2(ArgModel):
    infile: None | Path = None


class Args3(ArgModel):
    infile: None | Path | str = None


def test_help(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(args=["--help"])
    assert capsys.readouterr().out == snapshot


def test_help_2(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args2.argparse(args=["--help"])
    assert capsys.readouterr().out == snapshot


def test_help_3(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(
        TypeError,
        match="Annotation is not callable: None | pathlib.Path | str on field Args3.infile",
    ):
        Args3.argparse(args=[])
    assert capsys.readouterr().out == snapshot


def test_parse() -> None:
    args = Args.argparse(args=[])
    assert args == Args(infile=None)

    args = Args.argparse(args=["--infile", "puppy"])
    assert args == Args(infile=Path("puppy"))
