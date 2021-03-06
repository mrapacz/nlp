import os, json

import regex
from gensim.models import Phrases
from tqdm import tqdm

word_pattern = "\p{Letter}+"
DATA_DIR = "/home/m.rapacz/Downloads/data/json"

phrases = Phrases()

import subprocess


def get_sum_data(files):
    sizes = subprocess.check_output(
        'du -s {}'.format(" ".join([file for file in files])),
        shell=True
    ).decode()
    lines = sizes.split("\n")
    tuples = [x.split('\t') for x in lines]
    tuples = [tuple for tuple in tuples if tuple != ['']]
    sizes, _ = zip(*tuples)
    size = sum([int(size) for size in sizes])
    return size


def load_data(gb=1):
    total_judgments = []
    files = os.listdir(DATA_DIR)

    analyzed_files = []
    with tqdm(total=100) as bar:
        last_value = 0
        for file in files:
            if file.startswith("judgment"):
                file_path = os.path.join(DATA_DIR, file)

                with open(file_path, 'r') as f:
                    data = json.load(f)
                    judgments = [x["textContent"] for x in data["items"]]
                total_judgments += judgments
                analyzed_files.append(file_path)

            if analyzed_files:
                percentage_loaded = int(get_sum_data(analyzed_files) / 1024 / 1024 / gb * 100)
                interval = percentage_loaded - last_value

                bar.update(interval)
                last_value = percentage_loaded

                if percentage_loaded >= 100:
                    break

    total_words = []

    for judgment in tqdm(total_judgments):
        judgment = regex.sub("<.*?>", "", judgment)
        judgment = regex.sub("-\n(\p{Letter}+)", r"\1", judgment)
        judgment = judgment.lower()

        words = []
        for match in regex.finditer(word_pattern, judgment):
            words += match.captures()

        total_words.append(words)
    return total_words
