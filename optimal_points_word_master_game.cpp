#include <map>
#include <set>
#include <string>
#include <vector>
#include <tuple>
#include <fstream>
#include <unordered_set>
#include <unordered_map>
#include <iostream>
#include <algorithm>
#include <functional>
#include <cassert>

long double INF = 10000000000000;
const long double cost_sequence[6] = {0, 10, 5, 3, 1, INF};

template <class T> struct array2d {
    size_t rows, cols;
    std::vector<T> data;
    array2d() {};
    array2d(size_t rows, size_t cols) : rows(rows), cols(cols) {};
    void resize(size_t rows, size_t cols) {
        this->rows = rows;
        this->cols = cols;
        data.resize(rows * cols);
    }
    T* operator[](size_t index) {
        return &data[index * cols];
    }
};

struct state {
    int depth;
    std::unordered_set<int> hidden_words;
};


template <> struct std::hash<state> {
    size_t operator()(const state &s) const {
        size_t hash = 0;
        for (auto it = s.hidden_words.begin(); it != s.hidden_words.end(); it++) {
            hash ^= *it;
        }
        size_t out_hash = s.depth ^ hash;
        return out_hash;
    }
};


bool operator==(const state &s1, const state &s2) {
    if (s1.depth != s2.depth) {
        return false;
    }
    if (s1.hidden_words.size() != s2.hidden_words.size()) {
        return false;
    }
    for (auto it = s1.hidden_words.begin(); it != s1.hidden_words.end(); it++) {
        if (s2.hidden_words.find(*it) == s2.hidden_words.end()) {
            return false;
        }
    }
    return true;
}

array2d<int> colourings;
std::vector<std::string> all_hidden_words;
std::vector<std::string> all_test_words;
std::unordered_map<int, int> hidden_to_test;
std::unordered_map<int, int> test_to_hidden;



int get_colouring(std::string &hidden, std::string &test) {
    char t[5], h[5];
    memcpy(t, test.c_str(), 5);
    memcpy(h, hidden.c_str(), 5);
    int s = 0;
    for (int k = 0, w = 1; k < 5; k++) {
        if (t[k] == h[k]) {
            t[k] = 254;
            h[k] = 255;
            s += 2 * w;
        }
        w *= 3;
    }
    for (int k = 0, w = 1; k < 5; k++) {
        for (int l = 0; l < 5; l++) {
            if (t[k] == h[l]) {
                h[l] = 255;
                s += w;
                break;
            }
        }
        w *= 3;
    }
    return s;
}

void initialise() {
    // load words from word_master_dictionary.txt, and store as a vector of strings
    std::ifstream hidden_file("word_master_dictionary.txt");
    std::string hidden_word;
    while (hidden_file >> hidden_word) {
        all_hidden_words.push_back(hidden_word);
    }
    hidden_file.close();
    std::ifstream test_file("BA_5_letter_dictionary.txt");
    std::string test_word;
    while (test_file >> test_word) {
        all_test_words.push_back(test_word);
    }
    test_file.close();
    
    for (int i = 0; i < all_hidden_words.size(); i++) {
        std::string word = all_hidden_words[i];
        for (int j = 0; j < all_test_words.size(); j++) {
            if (all_test_words[j] == word) {
                hidden_to_test[i] = j;
                test_to_hidden[j] = i;
                break;
            }
        }
    }
    // create a 2d array of colourings, and initialise to 0
    size_t num_hidden_words = all_hidden_words.size();
    size_t num_test_words = all_test_words.size();
    colourings.resize(num_hidden_words, num_test_words);
    for (int i = 0; i < num_hidden_words; i++) {
        for (int j = 0; j < num_test_words; j++) {
            colourings[i][j] = get_colouring(all_hidden_words[i], all_test_words[j]);
        }
    }
}

std::map<int, std::unordered_set<int>> get_transition_info(std::unordered_set<int> &curr_state, int test_word) {
    std::map<int, std::unordered_set<int>> transition_info;
    for (auto it: curr_state) {
        int colouring = colourings[test_to_hidden[it]][test_word];
        if (transition_info.find(colouring) == transition_info.end()) {
            transition_info[colouring] = std::unordered_set<int>();
        }
        transition_info[colouring].insert(it);
    }
    return transition_info;
}


std::tuple<long double, int> compute_value_function(int t, 
                                               std::unordered_set<int> &curr_state, 
                                               std::unordered_set<int> &test_words,
                                               std::unordered_map<state, std::tuple<long double, int>> &cache) {
    if (t == 5) {
        return std::make_tuple(INF, -1);
    }
    if (t == 4 && curr_state.size() != 1) {
        return std::make_tuple(INF, -1);
    }
    state curr = {t, curr_state};
    if (t == 4) {
        cache[curr] = std::make_tuple(cost_sequence[t], *curr_state.begin());
        return std::make_tuple(cost_sequence[t], *curr_state.begin());
    }
    if (curr_state.size() == 1) {
        cache[curr] = std::make_tuple(cost_sequence[t], *curr_state.begin());
        return std::make_tuple(cost_sequence[t], *curr_state.begin());
    }
    if (curr_state.size() == 2) {
        cache[curr] = std::make_tuple(cost_sequence[t] + cost_sequence[t + 1]/2, *curr_state.begin());
        return std::make_tuple(cost_sequence[t] + cost_sequence[t + 1]/2, *curr_state.begin());
    }
    if (cache.find(curr) != cache.end()) {
        return cache[curr];
    }
    long double state_value = INF;
    int best_word = -1;
    long double state_size = curr_state.size();
    std::vector<int> test_words_order;
    for (auto it = curr_state.begin(); it != curr_state.end(); it++) {
        test_words_order.push_back(*it);
    }
    for (auto it = test_words.begin(); it != test_words.end(); it++) {
        if (curr_state.find(*it) == curr_state.end()) {
            test_words_order.push_back(*it);
        }
    }
    for (auto it = test_words_order.begin(); it != test_words_order.end(); it++) {
        if (t == 0) {
            std::cout << "Checking " << all_test_words[*it] << std::endl;
        }
        long double curr_cost = cost_sequence[t];
        std::map<int, std::unordered_set<int>> next_states = get_transition_info(curr_state, *it);
        if (next_states.size() == 1) {
            continue;
        }
        bool exact_comp_req = false;
        for (auto it2 = next_states.begin(); it2 != next_states.end(); it2++) {
            int colouring = it2->first;
            if (colouring == 242) {
                continue;
            }
            if (curr_cost >= state_value) {
                break;
            }
            std::unordered_set<int> next_state = it2->second;
            long double next_state_size = next_state.size();
            if (next_state_size >= 3) {
                exact_comp_req = true;
            }
            curr_cost += next_state_size/state_size * (cost_sequence[t + 1] + cost_sequence[t + 2] * (1 - 1/next_state_size));
        }

        if (exact_comp_req) {
            for (auto it2 = next_states.begin(); it2 != next_states.end(); it2++) {
                int colouring = it2->first;
                if (colouring == 242) {
                    continue;
                }
                if (curr_cost >= state_value) {
                    break;
                }
                std::unordered_set<int> next_state = it2->second;
                long double next_state_size = next_state.size();
                std::tuple<long double, int> next_state_value = compute_value_function(t + 1, next_state, test_words, cache);
                long double next_state_value_first = std::get<0>(next_state_value);
                if (next_state_value_first >= 50) {
                    curr_cost = INF;
                }
                else {
                    curr_cost += next_state_size/state_size * (next_state_value_first - (cost_sequence[t + 1] + cost_sequence[t + 2] * (1 - 1/next_state_size)));
                }
            }
        }
        if (curr_cost < state_value) {
            state_value = curr_cost;
            best_word = *it;
            if (t == 0) {
                std::cout << "New best word: " << all_test_words[best_word] << " with score " << state_value << std::endl;
            }
        }
    }
    cache[curr] = std::make_tuple(state_value, best_word);
    return std::make_tuple(state_value, best_word);
}


std::string decode_colouring(int colouring) {
    char out[6] = "";
    out[5] = 0;
    int c = colouring;
    for (int i = 0; i < 5; i++) {
        out[i] = "BSG"[c % 3];
        c /= 3;
    }
    return std::string(out);
}


int encode_colouring(std::string colouring) {
    int output = 0;
    for (int i = 4; i >= 0; i--) {
        output *= 3;
        output += colouring[i] == 'B' ? 0 : colouring[i] == 'S' ? 1 : 2;
    }
    return output;
}


class GameTree {
public:
    std::tuple<int, std::unordered_set<int>> curr_state;
    std::string action;
    int score;
    GameTree *parent;
    std::vector<GameTree*> children;
    GameTree(std::tuple<int, std::unordered_set<int>> curr_state, std::string action) : curr_state(curr_state), action(action), score(-1) {};
    GameTree(std::tuple<int, std::unordered_set<int>> curr_state, std::string action, int score, GameTree *parent) : curr_state(curr_state), action(action), score(score), parent(parent) {};
    void add_child(GameTree *child) {
        children.push_back(child);
        std::sort(children.begin(), children.end(), [](const GameTree *a, const GameTree *b) {
            int a_score = a->score;
            int b_score = b->score;
            std::string a_score_str = decode_colouring(a_score);
            std::string b_score_str = decode_colouring(b_score);
            std::reverse(a_score_str.begin(), a_score_str.end());
            std::reverse(b_score_str.begin(), b_score_str.end());
            return encode_colouring(a_score_str) < encode_colouring(b_score_str);
        });
    }
    std::string print_tree() {
        std::function<std::string(GameTree*, int)> recurse = [&](GameTree* child, int depth) {
            std::string out = "";
            if (child->score != -1) {
                out += decode_colouring(child->score) + std::to_string(depth) + " " + child->action + " ";
            }
            else {
                out += child->action + " ";
            }
            bool new_line_flag = false;
            for (int i = 0; i < child->children.size(); i++) {
                new_line_flag = true;
                out += recurse(child->children[i], depth + 1);
                if (i < child->children.size() - 1) {
                    out += "\n";
                    for (int j = 0; j < 13 * depth + 6; j++) {
                        out += " ";
                    }
                }
            }
            // get the set of words in the current state
            std::unordered_set<int> curr_words = std::get<1>(child->curr_state);
            // get index of action in all_test_words
            int action_index;
            for (int i = 0; i < all_test_words.size(); i++) {
                if (all_test_words[i] == child->action) {
                    action_index = i;
                    break;
                }
            }
            // check if child->action is in curr_words
            if (curr_words.find(action_index) != curr_words.end()) {
                if (!new_line_flag) {
                    out += "GGGGG" + std::to_string(depth+1);
                }
                else {
                    out += "\n";
                    for (int j = 0; j < 13 * depth + 6; j++) {
                        out += " ";
                    }
                    out += "GGGGG" + std::to_string(depth+1);
                }
            }
            return out;
        };
        return recurse(this, 0);
    }
};


int main() {
    initialise();
    std::cout << "Initialised" << std::endl;
    std::unordered_set<int> curr_state;
    for (int i = 0; i < all_hidden_words.size(); i++) {
        if (all_hidden_words[i][0] == 'S') {
            curr_state.insert(hidden_to_test[i]);
        }
    }
    std::cout << "Curr state size: " << curr_state.size() << std::endl;
    std::unordered_set<int> test_words;
    for (int i = 0; i < all_test_words.size(); i++) {
        test_words.insert(i);
    }
    std::cout << "Test words size: " << test_words.size() << std::endl;
    std::unordered_map<state, std::tuple<long double, int>> cache;
    std::tuple<long double, int> value = compute_value_function(0, curr_state, test_words, cache);
    long double value_first = std::get<0>(value);
    std::string value_second = all_test_words[std::get<1>(value)];
    std::cout << value_first << " " << value_second << std::endl;

    GameTree *root = new GameTree(std::make_tuple(0, curr_state), value_second);
    std::map<int, std::unordered_set<int>> transition_info1 = get_transition_info(curr_state, std::get<1>(value));
    for (auto it1 = transition_info1.begin(); it1 != transition_info1.end(); it1++) {
        if (it1->first == 242) {
            continue;
        }
        int best_word1_index;
        // print the current state
        if (it1->second.size() == 1) {
            best_word1_index = *it1->second.begin();
        }
        else {
            std::tuple<long double, int> value = compute_value_function(1, it1->second, test_words, cache);
            best_word1_index = std::get<1>(value);
        }
        std::string best_word1 = all_test_words[best_word1_index];
        GameTree *child1 = new GameTree(std::make_tuple(1, it1->second), best_word1, it1->first, root);
        root->add_child(child1);
        std::map<int, std::unordered_set<int>> transition_info2 = get_transition_info(it1->second, best_word1_index);
        for (auto it2 = transition_info2.begin(); it2 != transition_info2.end(); it2++) {
            if (it2->first == 242) {
                continue;
            }
            int best_word2_index;
            if (it2->second.size() == 1) {
                best_word2_index = *it2->second.begin();
            }
            else {
                best_word2_index = std::get<1>(compute_value_function(2, it2->second, test_words, cache));
            }
            std::string best_word2 = all_test_words[best_word2_index];
            GameTree *child2 = new GameTree(std::make_tuple(2, it2->second), best_word2, it2->first, child1);
            child1->add_child(child2);
            std::map<int, std::unordered_set<int>> transition_info3 = get_transition_info(it2->second, best_word2_index);
            for (auto it3 = transition_info3.begin(); it3 != transition_info3.end(); it3++) {
                if (it3->first == 242) {
                    continue;
                }
                int best_word3_index;
                if (it3->second.size() == 1) {
                    best_word3_index = *it3->second.begin();
                }
                else {
                    best_word3_index = std::get<1>(compute_value_function(3, it3->second, test_words, cache));
                }
                std::string best_word3 = all_test_words[best_word3_index];
                GameTree *child3 = new GameTree(std::make_tuple(3, it3->second), best_word3, it3->first, child2);
                child2->add_child(child3);
                std::map<int, std::unordered_set<int>> transition_info4 = get_transition_info(it3->second, best_word3_index);
                for (auto it4 = transition_info4.begin(); it4 != transition_info4.end(); it4++) {
                    if (it4->first == 242) {
                        continue;
                    }
                    int best_word4_index;
                    if (it4->second.size() == 1) {
                        best_word4_index = *it4->second.begin();
                    }
                    else {
                        best_word4_index = std::get<1>(compute_value_function(4, it4->second, test_words, cache));
                    }
                    std::string best_word4 = all_test_words[best_word4_index];
                    GameTree *child4 = new GameTree(std::make_tuple(4, it4->second), best_word4, it4->first, child3);
                    child3->add_child(child4);
                    std::map<int, std::unordered_set<int>> transition_info5 = get_transition_info(it4->second, best_word4_index);
                    for (auto it5 = transition_info5.begin(); it5 != transition_info5.end(); it5++) {
                        if (it5->first == 242) {
                            continue;
                        }
                        int best_word5_index;
                        if (it5->second.size() == 1) {
                            best_word5_index = *it5->second.begin();
                        }
                        else {
                            best_word5_index = std::get<1>(compute_value_function(5, it5->second, test_words, cache));
                        }
                        std::string best_word5 = all_test_words[best_word5_index];
                        GameTree *child5 = new GameTree(std::make_tuple(5, it5->second), best_word5, it5->first, child4);
                        child4->add_child(child5);
                    }
                }
            }
        }
    }
    std::cout << root->print_tree() << std::endl;
    return 0;
}