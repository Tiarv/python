#!/usr/bin/env python3

import json
import os
import random
import sys
import time
import termios
import tty

# Georgian alphabet and corresponding names
mkhedruli_alphabet = {
    "ა": "[a]   ani",
    "ბ": "[b]   bani",
    "გ": "[g]   gani",
    "დ": "[d]   doni",
    "ე": "[ɛ]   eni",
    "ვ": "[v]   vini",
    "ზ": "[z]   zeni",
    "თ": "[tʰ]  tani",
    "ი": "[i]   ini",
    "კ": "[kʼ]  k'ani",
    "ლ": "[l]   lasi",
    "მ": "[m]   mani",
    "ნ": "[n]   nari",
    "ო": "[o]   oni",
    "პ": "[pʼ]  p'ari",
    "ჟ": "[ʒ]   zhani",
    "რ": "[r]   rae",
    "ს": "[s]   sani",
    "ტ": "[tʼ]  t'ari",
    "უ": "[u]   uni",
    "ფ": "[pʰ]  pari",
    "ქ": "[kʰ]  kani",
    "ღ": "[ɣ]   ghani",
    "ყ": "[qʼ]  q'ari",
    "შ": "[ʃ]   shini",
    "ჩ": "[t͡ʃʰ] chini",
    "ც": "[t͡sʰ] tsani",
    "ძ": "[d͡z]  dzili",
    "წ": "[t͡sʼ] ts'ili",
    "ჭ": "[t͡ʃʼ] ch'ari",
    "ხ": "[x]   khani",
    "ჯ": "[d͡ʒ]  jani",
    "ჰ": "[h]   hae"
}

STATS_FILE = "mkhedruli_stats.json"

def clear_screen():
    os.system('clear')

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            # If the file exists but cannot be parsed as JSON, delete it
            os.remove(STATS_FILE)
    return {char: {"correct": 0, "incorrect": 0} for char in mkhedruli_alphabet}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def calculate_error_rates(stats, exponent=0.5, default_error_rate=0.5):
    error_rates = {}
    for char, stat in stats.items():
        total_attempts = stat["correct"] + stat["incorrect"]
        if total_attempts > 0:
            error_rates[char] = (stat["incorrect"] / total_attempts) ** exponent
        else:
            error_rates[char] = default_error_rate
    return error_rates

def weighted_random_choice(items, weights):
    return random.choices(items, weights, k=1)[0]

def choose_character(stats):
    error_rates = calculate_error_rates(stats)
    characters = list(mkhedruli_alphabet.keys())
    weights = [error_rates[char] for char in characters]
    return weighted_random_choice(characters, weights)

def show_question(character, options):
    clear_screen()
    print(f"[ Press q to save stats and quit ]\n")
    print(f"Identify the name of the following Georgian character:\n\n{character}\n")
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

def blink(color):
    if color == "green":
        print("\033[32mCorrect!\033[0m")
    elif color == "red":
        print("\033[31mIncorrect!\033[0m")
    time.sleep(0.4)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    stats = load_stats()

    while True:
        character = choose_character(stats)
        correct_name = mkhedruli_alphabet[character]
        incorrect_names = random.sample([name for name in mkhedruli_alphabet.values() if name != correct_name], 3)
        options = [correct_name] + incorrect_names
        random.shuffle(options)

        show_question(character, options)

        user_input = getch()

        if user_input == 'q':
            save_stats(stats)
            break

        if '1' <= user_input <= '4' and options[int(user_input) - 1] == correct_name:
           blink("green")
           stats[character]["correct"] += 1
        else:
           blink("red")
           stats[character]["incorrect"] += 1

if __name__ == "__main__":
    main()
