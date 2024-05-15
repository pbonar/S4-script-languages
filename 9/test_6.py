import ipaddress
import pytest

from l6 import Error, OtherInfo, PasswordAccepted, PasswordRejected, SSHLogJournal


def test_parse_time():
    journal = SSHLogJournal()
    entry = journal.parse_log("Dec 10 10:54:29 LabSZ sshd[24868]: Received disconnect from 183.62.140.253: 11: Bye Bye [preauth]")

    assert entry.time.strftime("%b %d %H:%M:%S") == "Dec 10 10:54:29"


def test_valid_ip():
    IP = "173.234.31.186"
    
    journal = SSHLogJournal()
    entry = journal.parse_log(f"Dec 10 06:55:48 LabSZ sshd[24200]: Failed password for invalid user webmaster from {IP} port 38926 ssh2")
    
    assert entry.has_ip
    assert entry._extract_ip() == ipaddress.IPv4Address(IP)


def test_wrong_ip():
    journal = SSHLogJournal()
    entry = journal.parse_log("Dec 10 06:55:48 LabSZ sshd[24200]: Failed password for invalid user webmaster from 666.777.88.213 port 38926 ssh2")

    has = entry.has_ip
    assert not has

def test_no_ip():
    journal = SSHLogJournal()
    entry = journal.parse_log("Dec 10 10:54:29 LabSZ sshd[24870]: input_userauth_request: invalid user dff [preauth]")
    
    assert not entry.has_ip


@pytest.mark.parametrize(
    "log_line, expected",
    [
        ("Dec 10 07:07:45 LabSZ sshd[24206]: Failed password for invalid user test9 from 52.80.34.196 port 36060 ssh2", PasswordRejected),
        ("Dec 10 09:32:20 LabSZ sshd[24680]: Accepted password for fztu from 119.137.62.142 port 49116 ssh2", PasswordAccepted),
        ("Dec 10 11:03:40 LabSZ sshd[25448]: error: Received disconnect from 103.99.0.122: 14: No more user authentication methods available. [preauth]", Error),
        ("Dec 10 11:03:41 LabSZ sshd[25455]: pam_unix(sshd:auth): check pass; user unknown", OtherInfo)
    ]
)
def test_append(log_line, expected):
    journal = SSHLogJournal()
    journal.append(log_line)
    
    assert isinstance(journal[-1], expected)
