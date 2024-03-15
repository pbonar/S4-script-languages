import sys
from datetime import datetime
from typing import Tuple

def read_log() -> list[Tuple]:
    res: list[Tuple] = []
    
    for line in sys.stdin:
        tokens = line.rstrip().split()
        
        hostname: str = tokens[0]
        
        date_str = line.split("[")[1].split("]")[0]
        date: datetime = datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")
        
        request_details: str = line.split('"')[1].split('"')[0]
        
        status_code: int = int(tokens[-2])
        size: int | None = int(tokens[-1]) if tokens[-1] != "-" else None
        
        res.append((hostname, date, request_details, status_code, size))
    
    return res
        

def sort_log(log_list: list[Tuple], idx: int) -> list[Tuple]:
    if idx >= len(log_list[0]):
        raise ValueError("idx >= tuple size")
    
    return sorted(log_list, key=lambda x: x[idx])

def get_entries_by_addr(log_list: list[Tuple], hostname: str) -> list[Tuple]:
    return list(filter(lambda x: x[0] == hostname.rstrip(), log_list))

def get_entries_by_code(log_list: list[Tuple], status_code: int) -> list[Tuple]:
    return list(filter(lambda x: x[-2] == status_code, log_list))

def get_failed_reads(log_list: list[Tuple], joined: bool) -> list[Tuple] | Tuple[list[Tuple], list[Tuple]]:
    log_4xx = []
    log_5xx = []
    
    for log in log_list:
        if (log[-2] // 100) * 100 == 400:
            log_4xx.append(log)
        elif (log[-2] // 100) * 100 == 500:
            log_5xx.append(log)
            
    return log_4xx + log_5xx if joined else log_4xx, log_5xx

def get_entries_by_extension(log_list: list[Tuple], extention: str) -> list[Tuple]:
    return list(filter(lambda x: extention in x[2], log_list))

def print_entries(log_list: list[Tuple]) -> None:
    for log in log_list:
        print(log)

def main() -> None:
    log_list = read_log()
    
    # print(log_list)
    # print(sort_log(log_list, 6))
    # print(get_entries_by_addr(log_list, "burger.letters.com"))
    # print(get_entries_by_code(log_list, 404))
    # print(get_failed_reads(log_list, False))
    # print(get_entries_by_extension(log_list, "jpg"))
    # print_entries(log_list)

if __name__ == "__main__":
    main()
