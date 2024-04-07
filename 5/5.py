from datetime import datetime
from typing import TypedDict
import re
import logging
import sys
import random
import argparse


# Argparse
argparser = argparse.ArgumentParser(description="SSH Log Parser")
argparser.add_argument("file", type=str, help="Path to the log file")
argparser.add_argument("-v", "--verbosity", type=int, default=1, help="Logging verbosity level (-50)")

sub_parsers = argparser.add_subparsers(
    title="Mode",
    dest="mode",
    required=True
)

parser_print_parsed = sub_parsers.add_parser("print_parsed", help="Print parsed logs")
parser_print_random_user = sub_parsers.add_parser("random_user", help="Print n random logs for a random user")
parser_print_avg_session_duration = sub_parsers.add_parser("avg_session_duration", help="Print average session duration")
parser_print_most_least_logged_in_user = sub_parsers.add_parser("most_least_logged_in_user", help="Print most and least logged in user")

parser_print_random_user.add_argument("-n", "--number", type=int, help="Number of logs to print", required=True)
parser_print_avg_session_duration.add_argument("-u", "--user", type=str, help="User to calculate average session duration for", required=False)

args = argparser.parse_args()
# Argparse


# Logger
logger = logging.getLogger(__name__)
logger.setLevel(50 - args.verbosity * 10)

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.DEBUG)
h1.addFilter(lambda record: record.levelno <= logging.INFO)

h2 = logging.StreamHandler(sys.stderr)
h2.setLevel(logging.WARNING)

logger.addHandler(h1)
logger.addHandler(h2)
# Logger


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
        "details": second_half.strip()
    }


def get_ipv4s_from_log(entry: LogEntry) -> list[str]:
    ips = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", entry["details"])
    return list(ips) if ips else []


def get_user_from_log(entry: LogEntry) -> str | None:
    user = re.search(r"user (\w+)|user=(\w+)", entry["details"])
    return (user.group(1) or user.group(2)) if user else None


def get_message_type(entry: LogEntry) -> str:
    patterns = {
        "SessionOpened": r"pam_unix\(sshd:session\): session opened for user (\w+)",
        "AuthFailure": r"pam_unix\(sshd:auth\): authentication failure; (\w+) rhost=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        "WrongPassword": r"Failed password for (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        "SessionClosed": r"pam_unix\(sshd:session\): session closed for user (\w+)",
        "WrongUsername": r"Invalid user (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        "PossibleBreakIn": r"reverse mapping checking getaddrinfo for (\w+\.\w+\.\w+\.\w+) failed - POSSIBLE BREAK-IN ATTEMPT! user=(\w+)"
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


def calculate_avg_session_duration(logs: list[LogEntry]) -> float:
    duration = 0.0
    count = 0
    
    for log in logs:
        match get_message_type(log):
            case "SessionOpened":
                date = log["date"]
            case "SessionClosed":
                duration += (log["date"] - date).total_seconds()
                count += 1
    
    return duration / count if count > 0 else 0


def find_most_least_logged_in_user(logs: list[LogEntry]) -> tuple[str, str]:
    users: dict[str, int] = {}
    
    for log in logs:
        user = get_user_from_log(log)
        if user:
            if user not in users:
                users[user] = 0
            users[user] += 1
    
    most = max(users, key=users.__getitem__)
    least = min(users, key=users.__getitem__)
    
    return most, least


def parse_all(lines: list[str]) -> list[LogEntry]:
    entries: list[LogEntry] = []
    
    for line in lines:
        logger.debug(f"Bytes read: {len(line.encode('utf-8'))}")
        entry = parse_line(line)
        entries.append(entry)
        
        ip = get_ipv4s_from_log(entry)
        user = get_user_from_log(entry)
        message_type = get_message_type(entry)
        
        match message_type:
            case "SessionOpened":
                logger.info(f"SessionOpened: (IP: {ip}) (User: {user})")
            case "AuthFailure":
                logger.warning(f"AuthFailure: (IP: {ip}) (User: {user})")
            case "WrongPassword":
                logger.error(f"WrongPassword: (IP: {ip}) (User: {user})")
            case "PossibleBreakIn":
                logger.critical(f"PossibleBreakIn: (IP: {ip}) (User: {user})")
    
    return entries


def print_parsed(entries: list[LogEntry]) -> None:
    for entry in entries:
        ip = get_ipv4s_from_log(entry)
        user = get_user_from_log(entry)
        message_type = get_message_type(entry)
        
        print(f"(IP: {ip}) (User: {user}) (Message type: {message_type})")


def main() -> None:
    f = open("SSH.log", "r")
    entries = parse_all(f.readlines())
    
    match args.mode:
        case "print_parsed":
            print(">> Print parsed logs")
            print_parsed(entries)
        case "random_user":
            print(">> Print n random logs for a random user")
            logs = n_logs_for_random_user(entries, args.number, set(y for x in entries if (y := get_user_from_log(x)) is not None))
            for log in logs:
                print(log)
        case "avg_session_duration":
            if args.user:
                print(f">> Print average session duration for user {args.user}")
                print(f"{calculate_avg_session_duration(list(filter(lambda x: get_user_from_log(x) == args.user, entries)))} s")
            else:
                print(">> Print average session duration")
                print(f"{calculate_avg_session_duration(entries)} s")
        case "most_least_logged_in_user":
            print(">> Print most and least logged in user")
            
            most, least = find_most_least_logged_in_user(entries)
            
            print(f"Most logged in user: {most}")
            print(f"Least logged in user: {least}")
    
    f.close()


if __name__ == "__main__":
    main()
