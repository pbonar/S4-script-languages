# Funkcje filtrujące
# G)

import sys
from datetime import datetime
from typing import Iterable, Literal

def filter_day_of_the_week(lines: Iterable[str], day: Literal[0,1,2,3,4,5,6]) -> list[str]:
    res: list[str] = []
    
    for line in lines:
        date_str = line.split("[")[1].split(":")[0]
        date = datetime.strptime(date_str, "%d/%b/%Y")
        
        if date.weekday() == day:
            res.append(line.rstrip())
    
    return res

def main() -> None:
    try:
        lines = filter_day_of_the_week(sys.stdin, 4) # only friday
        
        for line in lines:
            print(line)
    except ValueError:
        print("Malformed data")

if __name__ == "__main__":
    main()
