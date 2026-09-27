"""crossmith-example-cli: the simplest possible case for the Python adapter
— a single-file CLI with no dependencies. Try it with Crossmith itself:

    crossmith build examples/python-cli
"""

import sys


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "world"
    print(f"Hello, {name}! This binary was built by Crossmith.")


if __name__ == "__main__":
    main()
