import os
import argparse

def print_path_dir() -> None:
    path = os.getenv("PATH")
    if path:
        directories = path.split(os.pathsep)
        for directory in directories:
            if directory != "":
                print(" -", directory)

def print_path_exe() -> None:
    path = os.getenv("PATH")
    if path:
        directories = path.split(os.pathsep)
        for directory in directories:
            print(directory)
            executables = [file for file in os.listdir(directory)
                           if os.path.isfile(os.path.join(directory, file))
                           and os.access(os.path.join(directory, file), os.X_OK)]
            for executable in executables:
                print(" -", executable)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Operacje na sciezkach")
    parser.add_argument("-d", help="Katalogi w zmiennej PATH", action="store_true")
    parser.add_argument("-e", help="Pliki wykonywalne w każdym katalogu z zmiennej PATH", action="store_true")

    args = parser.parse_args()

    if args.d:
        print("Katalogi w zmiennej PATH:")
        print_path_dir()
    elif args.e:
        print("Pliki wykonywalne w każdym katalogu z zmiennej PATH:")
        print_path_exe()
    else:
        parser.print_help()