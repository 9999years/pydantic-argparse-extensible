from argparse import ArgumentParser

from pydantic import Field
from argparse_pydantic import ArgModel


class Args(ArgModel):
    user: str = Field(description="""The username to connect to.""")

    host: str = Field(description="""The host to connect to.""")


def main() -> None:
    parser = ArgumentParser()
    Args.update_argparser(parser)
    args = parser.parse_args()
    args = Args.from_parsed_args(args)
    print(args)


if __name__ == "__main__":
    main()
