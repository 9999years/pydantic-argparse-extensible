from pydantic_argparse_extensible import ArgModel


class Args(ArgModel):
    force: bool


def test_parse() -> None:
    args = Args.argparse(args=[])
    assert args == Args(force=False)

    args = Args.argparse(args=["--force"])
    assert args == Args(force=True)


def main() -> None:
    args = Args.argparse()
    print(args)


if __name__ == "__main__":
    main()
