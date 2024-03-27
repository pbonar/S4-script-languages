from datetime import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def log(dir: str, target_dir: str, date: str) -> None:
    try:
        with open(Path(target_dir, "backup.log").as_posix(), "r") as f:
            content = f.read()
    except:
        content = "[]"
    
    try: 
        data = json.loads(content)
    except:
        data = []
    
    entry = {
        "date": date,
        "filename": f"{date}.tar.gz",
        "copied_dir": os.path.abspath(dir)
    }
    data.append(entry)
    
    with open(Path(target_dir, "backup.log").as_posix(), "w") as f:
        f.write(json.dumps(data))

def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dir>")
        return
        
    to_copy_dir = sys.argv[1]
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    # tar
    subprocess.call(['tar', 'czf', f'{date}.tar.gz', to_copy_dir])

    # move file
    target_dir = os.environ["BACKUPS_DIR"] if "BACKUPS_DIR" in os.environ.keys() else Path(os.environ["HOME"], ".backups").as_posix()
    try:
        Path(target_dir).mkdir(exist_ok=True, parents=True)
        shutil.move(f"{date}.tar.gz", Path(target_dir, f"{date}.tar.gz").as_posix())
    except:
        print(f"Cannot write to {target_dir}")
        return
    
    # log in history
    log(to_copy_dir, target_dir, date)


if __name__ == "__main__":
    main()
