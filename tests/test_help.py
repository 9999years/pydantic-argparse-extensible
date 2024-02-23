import pytest
from pytest import CaptureFixture
from syrupy.assertion import SnapshotAssertion

from pydantic import Field
from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    user: str = Field(description="""The username to connect to.""")


def test_help(capsys: CaptureFixture, snapshot: SnapshotAssertion) -> None:
    with pytest.raises(SystemExit):
        Args.argparse(args=["--help"])
    assert capsys.readouterr().out == snapshot
