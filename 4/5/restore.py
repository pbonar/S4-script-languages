import glob
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from termcolor import colored


def main() -> None:
    if len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} <dir>")
        return
    
    default_dir = os.environ["BACKUPS_DIR"] if "BACKUPS_DIR" in os.environ.keys() else Path(os.environ["HOME"], ".backups").as_posix()
    backups_dir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    
    print(colored("-- All backups --", "green"))
    
    with open(Path(backups_dir, "backup.log").as_posix(), "r") as f:
        data = json.loads(f.read())
        
        for i, entry in enumerate(data):
            print(colored(f">>>> {i}.", "yellow"))
            print(colored(">", "cyan"), f"Date: {entry['date']}")
            print(colored(">", "cyan"), f"Filename: {entry['filename']}")
            print(colored(">", "cyan"), f"Copied dir: {entry['copied_dir']}")
        
        while True:
            try: 
                num_str = input(colored(">> Pick a backup number to restore: ", "yellow"))
                num = int(num_str)
                
                if num >= len(data):
                    print(colored(f"Out of range (0-{len(data)-1})", "red"))
                    continue
                
                # okay
                break
            except ValueError:
                print(colored("Invalid number", "red"))
                pass
                
        # delete current dir contents
        shutil.rmtree(data[num]["copied_dir"], ignore_errors=True)
            
        # untar the backup
        subprocess.call(['tar', 'xf', Path(backups_dir, data[num]["filename"]).as_posix(), '-C', Path(data[num]["copied_dir"]).parent.as_posix()])

        # print success
        print(colored("Restored!", "green"))

if __name__ == "__main__":
    main()
