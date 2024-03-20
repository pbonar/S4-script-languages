# Funkcje redukucjące
# A)

import sys
from typing import Iterable

def count_codes(lines: Iterable[str]) -> dict[int, int]:
    codes = {}

    for line in lines:
        tokens = line.split(" ")
        code = int(tokens[-2].strip())
        
        if code not in codes:
            codes[code] = 1
        else:
            codes[code] += 1
    
    return codes

def main() -> None:
    try:
        codes = count_codes(sys.stdin)
        
        if not 200 in codes.keys():
            codes[200] = 0
        if not 302 in codes.keys():
            codes[302] = 0
        if not 404 in codes.keys():
            codes[404] = 0

        print(f"200: {codes[200]}")
        print(f"302: {codes[302]}")
        print(f"404: {codes[404]}")
    except ValueError:
        print("Malformed data")

if __name__ == "__main__":
    main()
