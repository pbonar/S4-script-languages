# Funkcje filtrujące
# E)

import sys
from typing import Iterable


def filter_code(lines: Iterable[str], search_code: int) -> list[str]:
    res: list[str] = []

    for line in lines:
        tokens = line.split(" ")
        code = tokens[-2]

        if code == search_code:
            res.append(line.rstrip())

    return res


def main() -> None:
    try:
        lines = filter_code(sys.stdin, "200")
        for line in lines:
            print(line)
    except ValueError:
        print("Malformed data")


if __name__ == "__main__":
    main()
