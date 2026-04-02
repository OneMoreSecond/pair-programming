from __future__ import annotations

import sys

from .cli import main as pair_main


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] != "pair":
        print(
            "This wrapper only supports `opencode pair ...`. Use `opencode pair <command>`.",
            file=sys.stderr,
        )
        return 2
    return pair_main(args[1:])


if __name__ == "__main__":
    raise SystemExit(main())
