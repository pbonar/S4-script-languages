# Funkcje redukujące
# C)

import sys
from typing import Iterable

def find_biggest(lines: Iterable[str]) -> dict[int, int]:
    current_size = 0
    current_address = ""
    for line in lines:
        tokens = line.split(" ")
        try:
            size = int(tokens[-1].strip())
            if size > current_size:
                current_size = size
                current_address = str(tokens[-4].strip())
        except:
            pass
    return current_address, current_size


def main() -> None:
    try:
        ans = find_biggest(sys.stdin)
        print("sciezka: ", ans[0], "\nwielkosc: ", ans[1])
    except ValueError:
        print("Malformed data")


if __name__ == "__main__":
    main()