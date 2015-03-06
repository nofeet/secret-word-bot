"""Load words from system word list into curated word queue."""

import random

from .bot import load_config

CONFIG_FILE = './config.json'
NUM_WORDS = 200


def load_words():
    config = load_config()
    with open(config['word_list']) as f:
        sample = random.sample(f.readlines(), NUM_WORDS)
    with open(config['word_queue'], 'a') as f:
        f.writelines(sample)

if __name__ == '__main__':
    load_words()
