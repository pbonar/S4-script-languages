# Funkcje filtrujące
# D)

import sys
from datetime import datetime
from typing import Iterable

def filter_top_domain(lines: Iterable[str], top_domain: str) -> list[str]:
    res: list[str] = []
    
    for line in lines:
        tokens = line.split(" ")
        domain = tokens[0]
        top = domain.split(".")[-1]
        
        if top == top_domain:
            res.append(line.rstrip())
    
    return res

def main() -> None:
    try:
        lines = filter_top_domain(sys.stdin, "pl") # only ending with .pl
        
        for line in lines:
            print(line)
    except ValueError:
        print("Malformed data")

if __name__ == "__main__":
    main()
