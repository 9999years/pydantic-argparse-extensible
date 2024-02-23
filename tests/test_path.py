from pathlib import Path

from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    infile: Path


def test_parse() -> None:
    args = Args.argparse(args=["--infile", "my_file.txt"])
    assert args == Args(infile=Path("my_file.txt"))
