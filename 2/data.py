# Funkcje redukucjące
# B)

import sys
from typing import Iterable

def sum_sizes(lines: Iterable[str]) -> int:
    bytes = 0

    for line in lines:
        tokens = line.split(" ")
        if tokens[-1].strip() == "-":
            # skip when no size (404)
            continue
        
        size = int(tokens[-1].strip())
        bytes += size
    
    return bytes

def main() -> None:
    bytes = sum_sizes(sys.stdin)        
    print(bytes)

if __name__ == "__main__":
    main()
