import sys

def main():
    codes = {}

    for line in sys.stdin:
        things = line.split(" ")
        code = things[-2]
        print(code)

if __name__ == "__main__":
    main()
