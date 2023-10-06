# Word_Master_BA1_Bot
Two bots that play the Word Master minigame on Bookworm Adventures Volume 1. The first one plays deterministically, maximising entropy for guesses, and saving to memory once found. The second plays optimally, minimising the number of guesses, as determined by computing a full game tree.

To play, launch Bookworm Adventures 1, and get onto the screen for Word Master. Run either entropy_maximising_word_master_solver.py or optimal_word_master_solver.py and go back to the game screen. The bot will launch and locate the game, and begin by reading through every tile to determine what each tile looks like (it uses a single pixel to identify each pixel). Afterwards, it will start playing properly and you can leave it for however long you want.
