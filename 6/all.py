from abc import ABC, abstractmethod
from ipaddress import IPv4Address
import re


class SSHLogEntry(ABC):
    def __init__(self, time, raw_content, pid, host):
        self.time = time
        self.pid = pid
        self.host = host
        self._raw_content = raw_content

    def __str__(self):
        return f"Type: {self.type()} Time: {self.time}, Host: {self.host}, PID: {self.pid}, Raw Content: {self._raw_content}"

    @abstractmethod
    def validate(self):
        pass

    def type(self):
        return self.__class__.__name__

    @property
    def has_ip(self):
        return self._extract_ip() is not None

    def _extract_ip(self):
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_matched = re.search(ip_pattern, self._raw_content)
        if ip_matched:
            return IPv4Address(ip_matched.group())
        else:
            return None

    def __repr__(self):
        return f"{self.type()} >> time = {self.time}, host = {self.host}, pid = {self.pid}, raw_content = {self._raw_content}"

    def __eq__(self, other):
        return (isinstance(other, SSHLogEntry)
                and self.time == other.time
                and self._raw_content == other._raw_content
                and self.pid == other.pid)

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return self.time > other.time


class PasswordRejected(SSHLogEntry):
    def __init__(self, time, raw_content, pid, host):
        super().__init__(time, raw_content, pid, host)

    def validate(self):
        return "failed password" in self._raw_content.lower()


class PasswordAccepted(SSHLogEntry):
    def __init__(self, time, raw_content, pid, host):
        super().__init__(time, raw_content, pid, host)

    def validate(self):
        return "accepted password" in self._raw_content.lower()


class Error(SSHLogEntry):
    def __init__(self, time, raw_content, pid, host):
        super().__init__(time, raw_content, pid, host)

    def validate(self):
        return "error" in self._raw_content.lower()

class OtherInfo(SSHLogEntry):
    def __init__(self, time, raw_content, pid, host):
        super().__init__(time, raw_content, pid, host)

    def validate(self):
        return True

class SSHLogJournal:
    def __init__(self):
        self._log_entries = []

    def __len__(self):
        return len(self._log_entries)

    def __iter__(self):
        return iter(self._log_entries)

    def __contains__(self, item):
        return item in self._log_entries

    def parse_log(self, log):
        parts = log.split(" ")
        time = " ".join(parts[:3])
        host = parts[3]
        pid = parts[4][1:-1]
        raw_content = " ".join(parts)
        if "failed password" in raw_content.lower():
            entry = PasswordRejected(time, raw_content, pid, host)
        elif "accepted password" in raw_content.lower():
            entry = PasswordAccepted(time, raw_content, pid, host)
        elif "error" in raw_content.lower():
            entry = Error(time, raw_content, pid, host)
        else:
            entry = OtherInfo(time, raw_content, pid, host)

        return entry

    def append(self, log):
        entry = self.parse_log(log)

        if entry.validate():
            self._log_entries.append(entry)
        else:
            print("Invalid log entry:", log)

    def get_logs_by_string(self, criteria):
        filtered_logs = []
        for entry in self._log_entries:
            if criteria in entry._raw_content:
                filtered_logs.append(entry)
        return filtered_logs
    def print(self):
        for entry in journal:
            print(entry)

    def search_entry_log(self, log):
        entry = self.parse_log(log)
        return entry in journal

    def search_entry(self, time, raw_content, pid, host):
        if "failed password" in raw_content.lower():
            entry = PasswordRejected(time, raw_content, pid, host)
        elif "accepted password" in raw_content.lower():
            entry = PasswordAccepted(time, raw_content, pid, host)
        elif "error" in raw_content.lower():
            entry = Error(time, raw_content, pid, host)
        else:
            entry = OtherInfo(time, raw_content, pid, host)
        return entry in journal

# init
journal = SSHLogJournal()
file_path = "S4/SSH_shorter.log"
with open(file_path, 'r') as file:
    log_lines = file.readlines()
for line in log_lines:
    journal.append(line)

# tests
# dlugosc dziennika
print("Długość dziennika:", len(journal))

# dziennik
journal.print()

# logi w ktorych jest jakas fraza
print("Logi zawierające 'Failed password':", journal.get_logs_by_string("Failed password"))
print("Logi zawierające 'disconnect':", journal.get_logs_by_string("disconnect"))

print("Czy dziennik zawiera określony wpis:", journal.search_entry("Dec 10 09:12:48",
                                "Dec 10 09:12:48 LabSZ sshd[24503]: Received disconnect from 187.141.143.180: 11: Bye Bye [preauth]",
                                "shd[24503]", "LabSZ"))

print("Czy dziennik zawiera określony wpis:", journal.search_entry_log("Dec 10 09:12:48 LabSZ sshd[24503]: Received disconnect from 187.141.143.180: 11: Bye Bye [preauth]"))