# Funkcje redukujące
# D)

import sys
from typing import Iterable

def find_ratio(lines: Iterable[str]) -> float:
    total_req = 0
    image_req = 0
    for line in lines:
        tokens = line.split(" ")
        total_req += 1
        if tokens[-4].endswith((".gif", ".jpg", ".jpeg", ".xbm")):
            image_req += 1
    return image_req/total_req


def main() -> None:
    try:
        ans = find_ratio(sys.stdin)
        print(f"stosunek pobran grafiki do innych rzeczy: {ans:.2f}")
    except ValueError:
        print("Malformed data")


if __name__ == "__main__":
    main()