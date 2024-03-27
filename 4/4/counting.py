import json
import sys
import os
from collections import Counter

def analyze_file(file_path):
    with open(file_path, 'r') as file:

        content = file.read()

        total_characters = len(content)
        total_words = len(content.split())
        total_lines = content.count('\n') + 1

        character_frequency = Counter(content)
        most_common_character = character_frequency.most_common(1)[0][0]

        words = content.split()
        word_frequency = Counter(words)
        most_common_word = word_frequency.most_common(1)[0][0]

        return {
            'path': file_path,
            'total_characters': total_characters,
            'total_words': total_words,
            'total_lines': total_lines,
            'most_common_character': most_common_character,
            'most_common_word': most_common_word
        }

def main():

    # file_path = input("Podaj sciezke do pliku")
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        # print("Podany plik nie istnieje.")
        return

    result = analyze_file(file_path)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
