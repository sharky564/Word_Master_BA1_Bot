from math import inf, log2
from collections import Counter
from BA_read_tiles import *


word_master_target_dictionary = []
with open("word_master_dictionary.txt") as f:
    lines = f.readlines()
    for line in lines:
        word_master_target_dictionary.append(line.strip())

word_master_word_dictionary = []
with open("BA_5_letter_dictionary.txt") as f:
    lines = f.readlines()
    for line in lines:
        word = line.strip()
        word_master_word_dictionary.append(word)

def output(target: str, guess: str, known: dict[tuple[str, str], int]={}) -> int:
	if (target, guess) not in known:
		wrong = [i for i, v in enumerate(guess) if v != target[i]]
		counts = Counter(target[i] for i in wrong)
		out = 682
		for i in wrong:
			v = guess[i]
			if counts[v] > 0:
				out -= pow(4, i)
				counts[v] -= 1
			else:
				out -= 2 * pow(4, i)
		known[(target, guess)] = out
	return known[(target, guess)]

def convert_to_int(result: str) -> int:
    out = 0
    for i, char in enumerate(result):
        if char == "G":
            out += 2 * 4 ** i
        elif char == "S":
            out += 4 ** i
    return out


class Tree():
    def __init__(self, value: str, parent=None):
        self.value = value
        self.parent = parent
        self.children: dict[int, Tree] = dict()
        self.depth = 0
        if parent is not None:
            self.depth = parent.depth + 1

    def add_child(self, key: int, value: str):
        self.children[key] = Tree(value, self)

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def get_value(self):
        return self.value
    
    def __str__(self) -> str:
        def recur(curr: Tree, depth: int) -> str:
            out = curr.get_value() + "\n"
            for key, child in curr.children.items():
                out += "      " + depth * "          " + (3 - len(str(key))) * " " + str(key) + " " + recur(child, depth + 1)
            return out
        return recur(self, 0)

full_game_tree: dict[str, Tree] = dict()
for char in 'ABCDEFGHIJKLMNOPQRSTUVWYZ':
    with open(f"Word_Master_Tree/tree_{char}.txt", "r") as f:
        lines = f.readlines()
        init_word = lines[0][:5]
        full_game_tree[char] = Tree(init_word)
        num_lines = len(lines)
        curr_word = full_game_tree[char]
        curr_depth = 0
        i = 0
        while i < num_lines:
            j = 6
            while j < len(lines[i]):
                while j < len(lines[i]) and lines[i][j] == " ":
                    j += 13
                if j < len(lines[i]):
                    result = convert_to_int(lines[i][j: j + 5])
                    if result != 682:
                        word = lines[i][j + 7: j + 12]
                        curr_word.add_child(result, word)
                        curr_word = curr_word.get_children()[result]
                        curr_depth += 1
                j += 13
            i += 1
            if i < num_lines:
                j = 6
                new_depth = 0
                if j < len(lines[i]):
                    while j < len(lines[i]) and lines[i][j] == " ":
                        j += 13
                        new_depth += 1
                for _ in range(curr_depth - new_depth):
                    curr_word = curr_word.get_parent()
                curr_depth = new_depth
                    


counter = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for word in word_master_target_dictionary:
    char = word[0]
    curr_word = full_game_tree[char]
    while curr_word.get_value() != word:
        curr_word = curr_word.get_children()[output(word, curr_word.get_value())]
    counter[curr_word.depth + 1] += 1

print(counter)
points = [10000, 5000, 2500, 1000, 500]
total = 0
for i in range(1, 6):
    total += counter[i] * points[i - 1]
# print(total)
print(total/sum(counter.values()))

running = True
if running:
    print("Starting bot")
    time.sleep(2)
    
    initial_img = pyautogui.screenshot(region=racks[0][0])
    pyautogui.click(left + 414, top + 214)
    order, identifier_pixel = letter_determiner()
    found = False
    initial_letter = " "
    for char in order:
        if initial_img.getpixel(identifier_pixel[char]) == (0, 0, 0):
            initial_letter = char
            print(initial_letter)
            found = True
            break
    if not found:
        raise ValueError("Cannot read tile")
    else:
        word_input(initial_letter)
    print("Bot initialised")
    while running:
        initial_img = pyautogui.screenshot(region=racks[0][0])
        found = False
        initial_letter = " "
        for char in order:
            if initial_img.getpixel(identifier_pixel[char]) == (0, 0, 0):
                initial_letter = char
                curr_tree = full_game_tree[initial_letter]
                print(initial_letter)
                found = True
                break
        if not found:
            print("Cannot read tile")
            break
        else:
            word_determined = False
            attempt = 0
            verdict = 0
            prev_best_word = initial_letter
            while not word_determined and attempt < 5:
                curr_best_word = curr_tree.get_value()
                inputs = []
                if attempt == 0:
                    if curr_best_word[0] != prev_best_word[0]:
                        pyautogui.click((left + 414, top + 214))
                    else:
                        inputs.append(0)
                else:
                    val = verdict
                    for i in range(5):
                        if val % 4 == 2:
                            if curr_best_word[i] != prev_best_word[i]:
                                pyautogui.click((left + 414 + 90 * i, top + 214 + 90 * attempt))
                            else:
                                inputs.append(i)
                        val //= 4
                word_input(''.join(char for i, char in enumerate(curr_best_word) if i not in inputs))
                prev_best_word = curr_best_word
                verdict = 0
                time.sleep(0.5)
                for i in range(5):
                    img = pyautogui.screenshot(region=racks[attempt][i])
                    verdict += convert_img_to_result(img) * pow(4, i)
                if any((verdict >> (2 * i)) % 4 == 3 for i in range(5)):
                    word_determined = True
                else:
                    curr_tree = curr_tree.get_children()[verdict]
                    attempt += 1
            if not word_determined:
                running = False