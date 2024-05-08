import sys
from datetime import datetime
from typing import TypedDict
import re
import random


LogEntry = TypedDict('LogEntry', {
    "date": datetime,
    "machine_name": str,
    "sshd_pid": int,
    "details": str
})

def parse_line(line: str) -> LogEntry:
    first_half = line.split("]: ")[0]
    second_half = line.split("]: ")[1]
    
    # Get the basic info from the first half
    info = re.search(r"(\w{3}\s*\d{1,2} \d{2}:\d{2}:\d{2}) (\w+) sshd\[(\d+)$", first_half)
    if info:
        date_str = info.group(1)
        machine_name = info.group(2)
        sshd_pid = int(info.group(3))
    else:
        print(first_half)
        raise ValueError("Invalid line")

    return {
        "date": datetime.strptime(date_str, "%b %d %H:%M:%S"),
        "machine_name": machine_name,
        "sshd_pid": sshd_pid,
        "details": second_half.strip(),
    }

#TO DO
def check_date(d_from: str, d_to: str, line: str) -> bool:
    try:
        date_from = datetime.strptime(d_from, "%b %d %H:%M:%S")
    except:
        date_from = None
    try:
        date_to = datetime.strptime(d_to, "%b %d %H:%M:%S")
    except:
        date_to = None

    date_act = parse_line(line)["date"]

    if date_to is not None:
        if date_from is not None:
            if date_to >= date_act and date_from <= date_act:
                return True
            else:
                return False
        else:
            if date_to >= date_act:
                return True
            else:
                return False
    else:
        if date_from is not None:
            if date_from <= date_act:
                return True
            else:
                return False
        else:
            return True


def get_log_size(line: str) -> str:
    return str(len(line.encode("utf-8"))) + " bytes"


def get_ipv4s_from_log(entry: LogEntry) -> list[str]:
    ips = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", entry["details"])
    return list(ips) if ips else  []


def get_user_from_log(entry: LogEntry) -> str | None:
    user = re.search(r"user (\w+)|user=(\w+)", entry["details"])
    return (user.group(1) or user.group(2)) if user else None


def get_message_type(entry: LogEntry) -> str:
    patterns = {
        "SessionOpened": r"pam_unix\(sshd:session\): session opened for user (\w+)",
        "AuthFailure": r"pam_unix\(sshd:auth\): authentication failure",
        "WrongPassword": r"Failed password for (\w+) from",
        "SessionClosed": r"pam_unix\(sshd:session\): session closed for user (\w+)",
        "WrongUsername": r"Invalid user (\w+) from",
        "PossibleBreakIn": r"failed - POSSIBLE BREAK-IN ATTEMPT!"
    }
    
    for key, pattern in patterns.items():
        if re.search(pattern, entry["details"]):
            return key
    
    return "other"


def n_logs_for_random_user(logs: list[LogEntry], n: int, users: set[str]) -> list[LogEntry]:
    # pick a random user
    user = random.choice(list(users))
    
    # get all logs for that user
    all = list(filter(lambda x: get_user_from_log(x) == user, logs))
    
    # return n random logs
    return random.sample(all, n if n <= len(all) else len(all))


def session_duration_stats(logs: list[LogEntry]) -> tuple[float, float]:
    durations: list[float] = []
    
    open_date: dict[str, datetime] = {}
    
    for log in logs:
        user = get_user_from_log(log)
        if not user:
            continue
        
        match get_message_type(log):
            case "SessionOpened":
                open_date[user] = log["date"]
            case "SessionClosed":
                if user in open_date:
                    durations.append((log["date"] - open_date[user]).total_seconds())
                    open_date.pop(user)

    average = sum(durations) / len(durations) if len(durations) > 0 else 0
    standard_deviation = (sum([(x - average) ** 2 for x in durations]) / len(durations)) ** 0.5 if len(durations) > 0 else 0
    
    return average, standard_deviation


def find_most_least_logged_in_user(logs: list[LogEntry]) -> tuple[str, str]:
    users: dict[str, int] = {}
    
    for log in logs:
        if "session opened" not in log["details"]:
            continue
        
        user = get_user_from_log(log)
        if user:
            if user not in users:
                users[user] = 0
            users[user] += 1
    
    most = max(users, key=users.__getitem__)
    least = min(users, key=users.__getitem__)
    
    return most, least


