import os
import subprocess
import json
import sys
from collections import Counter
from typing import Dict

def analyze_file(file_path) -> Dict:
    result = subprocess.run(["python3", "./4/4/counting.py", file_path], capture_output=True, text=True)
    print(result)
    output = json.loads(result.stdout)
    return output

def main(directory) -> None:
    list = []
    total_files = 0
    total_characters = 0
    total_words = 0
    total_lines = 0
    character_counter: Counter = Counter()
    word_counter: Counter = Counter()

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_path = file_path.replace('\\', '/')
            if os.path.isfile(file_path):
                total_files += 1
                print(file_path)
                file_info = analyze_file(file_path)

                total_characters += file_info['total_characters']
                total_words += file_info['total_words']
                total_lines += file_info['total_lines']
                character_counter.update(file_info['most_common_character'])
                word_counter.update(file_info['most_common_word'])

                list.append(file_info)

    most_common_character = character_counter.most_common(1)[0][0]
    most_common_word = word_counter.most_common(1)[0][0]

    result = {
        'total_files': total_files,
        'total_characters': total_characters,
        'total_words': total_words,
        'total_lines': total_lines,
        'most_common_character': most_common_character,
        'most_common_word': most_common_word
    }

    print(json.dumps(result, indent=4))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Brak argumentu.")
        sys.exit(1)
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print("Podany argument nie jest katalogiem.")
        sys.exit(1)
    main(directory)
