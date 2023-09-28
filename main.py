from word_master_solver import *
from BA_read_tiles import *
import pickle as pkl


if '__main__' == __name__:
    word_master_target_dictionary = []
    with open("word_master_bot/word_master_dictionary.txt") as f:
        lines = f.readlines()
        for line in lines:
            word_master_target_dictionary.append(line.strip())

    word_master_word_dictionary = []
    with open("word_master_bot/BA_5_letter_dictionary.txt") as f:
        lines = f.readlines()
        for line in lines:
            word = line.strip()
            word_master_word_dictionary.append(word)
    
    running = True
    known_cache = True
    cache = {}
    print("Starting bot")
    if not known_cache:
        for target in word_master_target_dictionary:
            c = target[0]
            verdict = 2
            states = {c + 4 * " ": verdict}
            while verdict != 682:
                tested_word = best_word(states, word_master_target_dictionary, word_master_word_dictionary, cache)
                verdict = output(target, tested_word)
                states[tested_word] = verdict
        with open("word_master_bot/cache.pkl", "wb") as f:
            pkl.dump(cache, f)

    with open("word_master_bot/cache.pkl", "rb") as f:
        cache = pkl.load(f)
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
                print(initial_letter)
                found = True
                break
        if not found:
            print("Cannot read tile")
            break
        else:
            target = initial_letter + " " * 4
            states = {target: 2}
            word_determined = False
            attempt = 0
            verdict = 0
            prev_best_word = initial_letter
            while not word_determined and attempt < 5:
                try:
                    curr_best_word = best_word(states, word_master_target_dictionary, word_master_word_dictionary, cache)
                except:
                    print(target, states)
                    raise
                curr_best_word = best_word(states, word_master_target_dictionary, word_master_word_dictionary, cache)
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
                # time.sleep(0.5)
                for i in range(5):
                    img = pyautogui.screenshot(region=racks[attempt][i])
                    verdict += convert_img_to_result(img) * pow(4, i)
                states[curr_best_word] = verdict
                if any((verdict >> (2 * i)) % 4 == 3 for i in range(5)):
                    word_determined = True
                    if verdict != 1023:
                        print(states, verdict)
                else:
                    attempt += 1
            if not word_determined:
                running = False

