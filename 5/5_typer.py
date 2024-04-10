from datetime import datetime
from typing import TypedDict
import re
import logging
import sys
import random
import typer
from rich.console import Console
from rich.logging import RichHandler

console = Console()
app = typer.Typer()

# Konfiguracja loggera
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Dodanie RichHandler do loggera
rich_handler = RichHandler(show_time=False)
logger.addHandler(rich_handler)

state: dict[str, list] = {
    "entries": []
}

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
    user = random.choice(list(users))
    all = list(filter(lambda x: get_user_from_log(x) == user, logs))
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


def _print_parsed(entries: list[LogEntry]) -> None:
    for entry in entries:
        ip = get_ipv4s_from_log(entry)
        user = get_user_from_log(entry)
        message_type = get_message_type(entry)
        
        console.log(f">> ([bold]IP: {ip}[/bold]) (User: {user}) (Message type: {message_type})")


def _detect_bruteforce(entries: list[LogEntry], max_delay: int, max_attempts: int, user_to_detect: str | None) -> dict[str, int]:
    # Find the maximum chain of attempts for every IP
    # If the chain is longer than max_attempts, it's a bruteforce attack
    # If there's a delay longer than max_delay between attempts, it's a new chain
    
    longest_chains_for_ip: dict[str, int] = {}
    current_chains_for_ip: dict[str, int] = {}
    
    last_time_for_ip: dict[str, datetime] = {}

    for log in entries:
        ip = get_ipv4s_from_log(log)
        user = get_user_from_log(log)
        message_type = get_message_type(log)

        if user_to_detect and user != user_to_detect:
            continue

        if ip:
            if ip[0] not in longest_chains_for_ip:
                longest_chains_for_ip[ip[0]] = 0
                current_chains_for_ip[ip[0]] = 0

            if message_type == "AuthFailure":
                if ip[0] not in last_time_for_ip or (log["date"] - last_time_for_ip[ip[0]]).total_seconds() > max_delay:
                    current_chains_for_ip[ip[0]] = 0

                last_time_for_ip[ip[0]] = log["date"]
                current_chains_for_ip[ip[0]] += 1

                if current_chains_for_ip[ip[0]] > longest_chains_for_ip[ip[0]]:
                    longest_chains_for_ip[ip[0]] = current_chains_for_ip[ip[0]]

    return dict(filter(lambda x: x[1] > max_attempts, longest_chains_for_ip.items()))


@app.command()
def print_parsed():
    console.log(">> [bold]Print parsed logs[/bold]")
    _print_parsed(state["entries"])


@app.command()
def random_user(number: int):
    console.log(f">> [bold]Print {number} random logs for a random user[/bold]")
    logs = n_logs_for_random_user(state["entries"], number, set(y for x in state["entries"] if (y := get_user_from_log(x)) is not None))
    for log in logs:
        console.print(log)


@app.command()
def print_session_stats(user: str = ""):
    if user != "":
        console.log(f">> [bold]Print session stats for user {user}[/bold]")
        avg, std = session_duration_stats(list(filter(lambda x: get_user_from_log(x) == user, state["entries"])))
        console.log(f"Average: {avg} s")
        console.log(f"Standard deviation: {std} s")
    else:
        console.log(">> [bold]Print session stats[/bold]")
        avg, std = session_duration_stats(state["entries"])
        console.log(f"Average: {avg} s")
        console.log(f"Standard deviation: {std} s")


@app.command()
def most_least_logged_in_user():
    console.log(">> [bold]Print most and least logged in user[/bold]")
    most, least = find_most_least_logged_in_user(state["entries"])
    console.log(f"Most logged in user: {most}")
    console.log(f"Least logged in user: {least}")


@app.command()
def detect_bruteforce(user: str = "", max_delay: int = 5, max_attempts: int = 3):
    console.log(f">> [bold]Detect bruteforce[/bold] - Max delay between attempts: {max_delay} seconds, Max attempts: {max_attempts}")
    attacks = _detect_bruteforce(state["entries"], max_delay=max_delay, max_attempts=max_attempts, user_to_detect=(user if user != "" else None))
    for ip, attempts in attacks.items():
        console.log(f"Bruteforce attack detected from {ip} ({attempts} attempts)")


@app.callback()
def main(log_file: str, verbosity: int = 0):
    # Ustawienie poziomu logowania na podstawie wartości verbosity
    logger.setLevel(51 - verbosity * 10)

    # Otwarcie pliku dziennika
    with open(log_file, "r") as f:
        entries = parse_all(f.readlines())
        state["entries"] = entries


if __name__ == "__main__":
    app()
