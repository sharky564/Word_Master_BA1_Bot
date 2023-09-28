from math import inf, log2
from collections import Counter


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

output_cache = {}
def pos_words(states: dict[str, int], target_dictionary: list[str]) -> list[str]:
	pos_words = []
	for word in target_dictionary:
		if all(output(word, target, output_cache) == states[target] for target in states):
			pos_words.append(word)
	return pos_words


def word_score(states: dict[str, int], target_dictionary: list[str], word_dictionary: list[str], num_letters: int=5) -> dict[str, tuple[float, bool]]:
	possible_words = pos_words(states, target_dictionary)
	score_dict = dict()
	num = len(possible_words)
	if num == 0:
		print(states)
		raise ValueError("No such word")
	elif num == 1:
		return {possible_words[0]: (float(inf), True)}
	else:
		count = 0
		for word in word_dictionary:
			state_freq = {}
			for pos_target in possible_words:
				state = output(pos_target, word)
				if state not in state_freq:
					state_freq[state] = 1
				else:
					state_freq[state] += 1
			score = sum(state_freq[state]/num * log2(num/state_freq[state]) for state in state_freq)
			count += 1
			score_dict[word] = (score, word in possible_words, len(set(word)) == num_letters)
		return score_dict


def best_word(states: dict[str, int], target_dictionary: list[str], word_dictionary: list[str], cache={}) -> str:
	if tuple(states.items()) not in cache:
		scores = word_score(states, target_dictionary, word_dictionary)
		output = max(scores.items(), key=lambda x: x[1])[0]
		cache[tuple(states.items())] = output
	return cache[tuple(states.items())]