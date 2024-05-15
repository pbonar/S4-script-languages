import ipaddress
from abc import ABC, abstractmethod
from datetime import datetime
from ipaddress import IPv4Address
import re
from typing import List, Union, Optional, Iterator, overload

class SSHLogEntry(ABC):
    def __init__(self, time: datetime, raw_content: str, pid: str, host: str) -> None:
        self.time: datetime = time
        self.pid: str = pid
        self.host: str = host
        self._raw_content: str = raw_content

    def __str__(self) -> str:
        return f"Type: {self.type()} Time: {self.time}, Host: {self.host}, PID: {self.pid}, Raw Content: {self._raw_content}"

    @abstractmethod
    def validate(self) -> bool:
        pass

    def type(self) -> str:
        return self.__class__.__name__

    @property
    def has_ip(self) -> bool:
        return self._extract_ip() is not None

    def _extract_ip(self) -> Optional[IPv4Address]:
        ip_pattern: str = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_matched: Optional[re.Match[str]] = re.search(ip_pattern, self._raw_content)
        if ip_matched:
            try:
                return IPv4Address(ip_matched.group())
            except ipaddress.AddressValueError:
                return None
        else:
            return None

    def __repr__(self) -> str:
        return f"{self.type()} >> time = {self.time}, host = {self.host}, pid = {self.pid}, raw_content = {self._raw_content}"

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, SSHLogEntry)
                and self.time == other.time
                and self._raw_content == other._raw_content
                and self.pid == other.pid)

    def __lt__(self, other: 'SSHLogEntry') -> bool:
        return self.time < other.time

    def __gt__(self, other: 'SSHLogEntry') -> bool:
        return self.time > other.time

class PasswordRejected(SSHLogEntry):
    def __init__(self, time: datetime, raw_content: str, pid: str, host: str) -> None:
        super().__init__(time, raw_content, pid, host)

    def validate(self) -> bool:
        return "failed password" in self._raw_content.lower()

class PasswordAccepted(SSHLogEntry):
    def __init__(self, time: datetime, raw_content: str, pid: str, host: str) -> None:
        super().__init__(time, raw_content, pid, host)

    def validate(self) -> bool:
        return "accepted password" in self._raw_content.lower()

class Error(SSHLogEntry):
    def __init__(self, time: datetime, raw_content: str, pid: str, host: str) -> None:
        super().__init__(time, raw_content, pid, host)

    def validate(self) -> bool:
        return "error" in self._raw_content.lower()

class OtherInfo(SSHLogEntry):
    def __init__(self, time: datetime, raw_content: str, pid: str, host: str) -> None:
        super().__init__(time, raw_content, pid, host)

    def validate(self) -> bool:
        return True

class SSHLogJournal:
    def __init__(self) -> None:
        self._log_entries: List[SSHLogEntry] = []

    def __len__(self) -> int:
        return len(self._log_entries)

    def __iter__(self) -> Iterator[SSHLogEntry]:
        return iter(self._log_entries)

    def __contains__(self, item: SSHLogEntry) -> bool:
        return item in self._log_entries

    def parse_log(self, log: str) -> SSHLogEntry:
        parts: List[str] = log.split(" ")
        if parts[1] == "":
            parts.pop(1)
        time_str: str = " ".join(parts[:3])
        host: str = parts[3]
        pid: str = parts[4][1:-1]
        raw_content: str = " ".join(parts[5:])
        time: datetime = datetime.strptime(f"{time_str} {datetime.now().year}", "%b %d %H:%M:%S %Y")

        if "failed password" in raw_content.lower():
            entry: SSHLogEntry = PasswordRejected(time, raw_content, pid, host)
        elif "accepted password" in raw_content.lower():
            entry = PasswordAccepted(time, raw_content, pid, host)
        elif "error" in raw_content.lower():
            entry = Error(time, raw_content, pid, host)
        else:
            entry = OtherInfo(time, raw_content, pid, host)

        return entry

    def append(self, log: str) -> None:
        entry: SSHLogEntry = self.parse_log(log)
        if entry.validate():
            self._log_entries.append(entry)
        else:
            print("Invalid log entry:", log)

    def get_logs_by_string(self, criteria: str) -> List[SSHLogEntry]:
        return [entry for entry in self._log_entries if criteria in entry._raw_content]

    def print(self) -> None:
        for entry in self:
            print(entry)

    def search_entry_log(self, log: str) -> bool:
        entry: SSHLogEntry = self.parse_log(log)
        return entry in self

    def search_entry(self, time: datetime, raw_content: str, pid: str, host: str) -> bool:
        if "failed password" in raw_content.lower():
            entry: SSHLogEntry = PasswordRejected(time, raw_content, pid, host)
        elif "accepted password" in raw_content.lower():
            entry = PasswordAccepted(time, raw_content, pid, host)
        elif "error" in raw_content.lower():
            entry = Error(time, raw_content, pid, host)
        else:
            entry = OtherInfo(time, raw_content, pid, host)
        return entry in self

    @overload
    def __getitem__(self, search: Union[slice, IPv4Address, str]) -> List[SSHLogEntry]: ...
    @overload
    def __getitem__(self, search: int) -> SSHLogEntry: ...
    
    def __getitem__(self, search: Union[slice, int, IPv4Address, str]) -> Union[SSHLogEntry, List[SSHLogEntry]]:
        if isinstance(search, slice):
            return self._log_entries[search.start:search.stop:search.step]
        elif isinstance(search, int):
            return self._log_entries[search]
        elif isinstance(search, IPv4Address):
            return [entry for entry in self._log_entries if entry.has_ip and entry._extract_ip() == search]
        elif isinstance(search, str):
            return [entry for entry in self._log_entries if search in entry.time.strftime("%b %d %H:%M:%S")]
        else:
            raise ValueError("Invalid argument type")

class SSHUser:
    def __init__(self, name: str, last_login: datetime) -> None:
        self.name: str = name
        self.last_login: datetime = last_login

    def __repr__(self) -> str:
        return f"SSHUser >> name = {self.name}, last_login = {self.last_login}"

    def validate(self) -> bool:
        return re.match(r'^[a-z_][a-z0-9_-]{0,31}$', self.name) is not None

def main() -> None:
    # init
    journal: SSHLogJournal = SSHLogJournal()
    file_path: str = "SSH.log"
    with open(file_path, 'r') as file:
        log_lines: List[str] = file.readlines()
    for line in log_lines:
        journal.append(line)

    # tests
    print("Długość dziennika:", len(journal))
    journal.print()

    # logi w których jest jakaś fraza
    print("Logi zawierające 'Failed password':", journal.get_logs_by_string("Failed password"))
    print("Logi zawierające 'disconnect':", journal.get_logs_by_string("disconnect"))

    print("Czy dziennik zawiera określony wpis:",
          journal.search_entry(datetime.strptime("Dec 10 09:12:48", "%b %d %H:%M:%S"),
                               "Dec 10 09:12:48 LabSZ sshd[24503]: Received disconnect from 187.141.143.180: 11: Bye Bye [preauth]",
                               "24503", "LabSZ"))

    print("Czy dziennik zawiera określony wpis:", journal.search_entry_log(
        "Dec 10 09:12:48 LabSZ sshd[24503]: Received disconnect from 187.141.143.180: 11: Bye Bye [preauth]"))

    # duck typing
    test: List[Union[SSHUser, SSHLogEntry]] = [
        SSHUser("user123", datetime.now()),
        SSHUser("admin", datetime.now()),
        SSHUser("1abc", datetime.now()),
        *journal[5:10]
    ]
    for a in test:
        print(a.validate())

if __name__ == "__main__":
    main()