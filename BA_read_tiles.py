'''
We will try to read the Bookworm Adventures rack
'''

# first we want to take a screenshot of the game
import pyautogui
import win32gui
import time
from PIL import Image


def get_window_rect(window_title):
    hwnd = win32gui.FindWindow(None, window_title)  # Find the window handle by its title
    if hwnd == 0:
        return None  # Window not found

    rect = win32gui.GetWindowRect(hwnd)  # Get the window's position and size
    left, top, right, bottom = rect  # Unpack the position and size

    return (left, top, right, bottom)


x = get_window_rect('Bookworm Adventures Deluxe 1.0 ')
if x is None:
    raise Exception('Window not found')
else:
    left, top, right, bottom = x


windows_unadjusted_racks = [
         [(380, 176, 75, 75), (468, 176, 75, 75), (557, 176, 75, 75), (645, 176, 75, 75), (734, 176, 75, 75)],
         [(380, 266, 75, 75), (468, 266, 75, 75), (557, 266, 75, 75), (645, 266, 75, 75), (734, 266, 75, 75)], 
         [(380, 356, 75, 75), (468, 356, 75, 75), (557, 356, 75, 75), (645, 356, 75, 75), (734, 356, 75, 75)], 
         [(380, 446, 75, 75), (468, 446, 75, 75), (557, 446, 75, 75), (645, 446, 75, 75), (734, 446, 75, 75)], 
         [(380, 536, 75, 75), (468, 536, 75, 75), (557, 536, 75, 75), (645, 536, 75, 75), (734, 536, 75, 75)]
         ]

racks = [[(left + x[0], top + x[1], x[2], x[3]) for x in row] for row in windows_unadjusted_racks]

windows_unadjusted_tiles = {char: (114 + 75 * (i % 13) + 38, 693 + 75 * (i//13) + 38) for i, char in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}

tiles = {char: (left + x[0], top + x[1]) for char, x in windows_unadjusted_tiles.items()}

windows_unadjusted_enter = (590, 900)
enter = (left + windows_unadjusted_enter[0], top + windows_unadjusted_enter[1])

# time.sleep(2)
# tile_size = (75, 75)
# for i in range(5):
#     for j in range(5):
#         pyautogui.screenshot(f'rack_imgs/BA_screenshot_{i}_{j}.png', region=racks[i][j])

# generate a frequency plot of the colours in the image
 
# get all rgb values in the image
def get_rgb(img):
    rgb_values = []
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            # check pixel is not black
            if img.getpixel((x, y)) != (0, 0, 0):
                rgb_values.append(img.getpixel((x, y)))
    return rgb_values


gold = (116, 114, 2)
silver = (239, 239, 239)
empty = (14, 9, 3)

def convert_img_to_result(img):
    # convert image to a list of rgb values
    rgb_values = get_rgb(img)
    # get the frequency of each rgb value
    rgb_freq = {}
    for rgb in rgb_values:
        if rgb in rgb_freq:
            rgb_freq[rgb] += 1
        else:
            rgb_freq[rgb] = 1
    # restrict to top 5 colours
    rgb_freq = dict(sorted(rgb_freq.items(), key=lambda x: x[1], reverse=True)[:30])
    # print(rgb_freq)
    if gold in rgb_freq:
        return 2
    elif silver in rgb_freq:
        return 1
    elif empty in rgb_freq:
        return 3
    else:
        return 0

# rgb_freq = {}
# img = Image.open('rack_imgs/BA_screenshot_4_1.png')
# rgb_values = get_rgb(img)
# for rgb in rgb_values:
#     if rgb in rgb_freq:
#         rgb_freq[rgb] += 1
#     else:
#         rgb_freq[rgb] = 1

# rgb_freq = dict(sorted(rgb_freq.items(), key=lambda x: x[1], reverse=True)[:10])
# print(rgb_freq)

# time.sleep(2)
# for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
#     # click the tile
#     pyautogui.click(tiles[char])
#     # move mouse away
#     pyautogui.moveTo(left + 100, top + 100)
#     # screenshot the tile
#     time.sleep(0.1)
#     img = pyautogui.screenshot(f'tile_imgs/BA_screenshot_{char}.png', region=racks[0][0])
#     pyautogui.click((left + 414, top + 214))
#     time.sleep(0.1)

def letter_determiner():
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        # click the tile
        pyautogui.click(tiles[char])
        # move mouse away
        pyautogui.moveTo(left + 100, top + 100)
        # screenshot the tile
        time.sleep(0.1)
        img = pyautogui.screenshot(f'tile_imgs/BA_screenshot_{char}.png', region=racks[0][0])
        pyautogui.click((left + 414, top + 214))
        time.sleep(0.1)
    all_pixels = {}
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        # get all pixels in the image
        img = Image.open(f'tile_imgs/BA_screenshot_{char}.png')
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if img.getpixel((x, y)) == (0, 0, 0):
                    if (x, y) not in all_pixels:
                        all_pixels[(x, y)] = [char]
                    else:
                        all_pixels[(x, y)].append(char)
    seen_pix = set()
    output = {}
    seen = ''
    while len(seen) < 26:
        for pixel in all_pixels:
            if len(all_pixels[pixel]) == 1 and pixel not in seen_pix:
                char = all_pixels[pixel][0]
                seen += char
                seen_pix.add(pixel)
                output[char] = pixel
                for c in all_pixels:
                    if char in all_pixels[c]:
                        all_pixels[c].remove(char)
    return seen, output


# all_pixels = {}
# for char in 'FIJL':
#     # get all pixels in the image
#     img = Image.open(f'tile_imgs/BA_screenshot_{char}.png')
#     pixels = []
#     for x in range(img.size[0]):
#         for y in range(img.size[1]):
#             if img.getpixel((x, y)) == (0, 0, 0):
#                 if (x, y) not in all_pixels:
#                     all_pixels[(x, y)] = [char]
#                 else:
#                     all_pixels[(x, y)].append(char)
# # print(all_pixels)

# seen = 'DKMOQVAGNWXHYRUZBCEPSTFIJL'
# seen_pix = set()
# for pixel in all_pixels:
#     if len(all_pixels[pixel]) == 1 and pixel not in seen_pix and all_pixels[pixel][0] not in seen:
#         seen += all_pixels[pixel][0]
#         seen_pix.add(pixel)
#         print(pixel, all_pixels[pixel])


# # identifier_pixel = {'A': (54, 52), 'B': (24, 24), 'C': (24, 33), 'D': (24, 23), 'G': (53, 39), 'H': (51, 41), 'K': (51, 53), 'M': (53, 26), 'N': (21, 24), 'O': (22, 37), 'P': (48, 35), 'Q': (32, 21), 'R': (23, 51), 'S': (48, 39), 'T': (24, 27), 'U': (50, 36), 'V': (51, 23), 'W': (17, 24), 'X': (22, 52), 'Y': (22, 24), 'Z': (51, 45)}
# identifier_pixel = {'D': (23, 23), 'K': (50, 53), 'M': (52, 26), 'O': (21, 37), 'Q': (31, 21), 'V': (50, 23), 'A': (53, 52), 'G': (52, 39), 'N': (20, 24), 'W': (16, 24), 'X': (21, 52), 'H': (50, 41), 'Y': (21, 24), 'R': (22, 51), 'U': (49, 23), 'Z': (50, 45), 'B': (23, 24), 'C': (23, 33), 'E': (47, 53), 'P': (47, 35), 'S': (47, 39), 'T': (23, 27), 'F': (25, 24), 'I': (37, 26), 'J': (25, 42), 'L': (28, 53)}
# order = 'DKMOQVAGNWXHYRUZBCEPSTFIJL'

# word_input("ANNEX")

# create new word_input function that does clicks as quickly as possible, but will wait 0.5 seconds if it detects a repeat letter using multithreading to keep track of when each letter was clicked

def word_input(word):
    blocked = {}
    def char_input(char):
        while char in blocked and abs(blocked[char] - time.time()) < 0.45:
            time.sleep(0.005)
        pyautogui.click(tiles[char])
        # blocked should contain the current time
        blocked[char] = time.time()
    
    for char in word:
        char_input(char)
    
    pyautogui.click(enter)
    time.sleep(0.2)

