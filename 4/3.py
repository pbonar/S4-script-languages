import argparse
import sys
import time
from typing import TextIO


parser = argparse.ArgumentParser(
    prog="Tail",
    description="Print the tail of a file"
)

parser.add_argument("filename", nargs="?", default=None)
parser.add_argument("-l", "--lines", default=10, type=int)
parser.add_argument('-f', '--follow', default=False, action='store_true')


def tail(file: TextIO, count: int, follow: bool) -> None:
    if count <= 0:
        return
    
    lines = file.readlines()
    for line in lines[-count:]:
        print(line, end="")
        
    if follow:
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
            else:
                sys.stdout.write(line)
                sys.stdout.flush()

def main() -> None:
    args = parser.parse_args()
    
    if args.filename is None:
        tail(sys.stdin, int(args.lines), args.follow)
    else:
        try:
            with open(args.filename, "r") as f:
                tail(f, int(args.lines), args.follow)
        except FileNotFoundError:
            print(f"File {args.filename} does not exist.")


if __name__ == "__main__":
    main()
