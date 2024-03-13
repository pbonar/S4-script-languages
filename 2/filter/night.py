# Funkcje filtrujące
# F)

import sys
from datetime import datetime
from typing import Iterable, Literal


def filter_hours(lines: Iterable[str]) -> list[str]:
    res: list[str] = []

    for line in lines:
        hour = int(line.split("[")[1].split(":")[1])

        if hour < 6 or hour >= 22:
            res.append(line.rstrip())

    return res


def main() -> None:
    try:
        lines = filter_hours(sys.stdin)
        for line in lines:
            print(line)
    except ValueError:
        print("Malformed data")


if __name__ == "__main__":
    main()
