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
num_options = 5
DISPLAY_OPTIONS_HORIZONTALLY = False
EXIT_KEY = "0"

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
    return {char: {"correct": 0, "incorrect": 0, "avg_time": None} for char in mkhedruli_alphabet}

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

def choose_character(stats, exponent=0.5, time_factor=0.1):
    error_rates = calculate_error_rates(stats, exponent=exponent)
    max_avg_time = max([stat.get("avg_time", 0) for stat in stats.values()])
    avg_times = {char: (stat.get("avg_time", 0) / max_avg_time) ** time_factor for char, stat in stats.items()}
    weights = [error_rates[char] + avg_times[char] for char in mkhedruli_alphabet.keys()]
    return weighted_random_choice(list(mkhedruli_alphabet.keys()), weights)

def show_question(character, options):
    clear_screen()
    print(f"[ Press {EXIT_KEY} to save stats and quit ]\n")
    print(f"Identify the name of the following Georgian character:\n\n{character}\n")
    if DISPLAY_OPTIONS_HORIZONTALLY:
        option_strings = [f"{i+1}. {option}" for i, option in enumerate(options)]
        print("  ".join(option_strings))
    else:
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")

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
        if ch == EXIT_KEY:
            clear_screen()
            sys.exit(0)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main():
    stats = load_stats()

    while True:
        character = choose_character(stats)
        correct_name = mkhedruli_alphabet[character]
        incorrect_names = random.sample([name for name in mkhedruli_alphabet.values() if name != correct_name], num_options - 1)
        options = [correct_name] + incorrect_names
        random.shuffle(options)

        show_question(character, options)

        start_time = time.time()
        answer = ""
        while not answer.isdigit() or not (1 <= int(answer) <= num_options):
            answer = getch()
        end_time = time.time()

        if answer == EXIT_KEY:
            break
        elif options[int(answer)-1] == correct_name:
            blink("green")
            time_diff = round(end_time - start_time, 2)
            if "avg_time" not in stats[character]:
                stats[character]["avg_time"] = None
            if stats[character]["avg_time"] is None:
                stats[character]["avg_time"] = time_diff
            else:
                prev_avg_time = stats[character]["avg_time"]
                stats[character]["avg_time"] = round((prev_avg_time + time_diff) / 2, 2)
            stats[character]["correct"] += 1
            answered_correctly = True
        else:
            blink("red")
            stats[character]["incorrect"] += 1
            answered_correctly = False

        if answer == EXIT_KEY:
            break

        if answered_correctly:
            save_stats(stats)

    save_stats(stats)
    sys.exit(0)


if __name__ == "__main__":
    main()
