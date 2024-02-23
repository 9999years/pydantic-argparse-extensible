from pydantic import Field

from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    host: str = Field(default_factory=lambda: "puppy")


def test_parse() -> None:
    args = Args.argparse(args=[])
    assert args == Args(host="puppy")

    args = Args.argparse(args=["--host", "doggy"])
    assert args == Args(host="doggy")
