# This trains and compiles the model into a folder
from concrete.ml.sklearn import NeuralNetRegressor
from concrete.ml.deployment import FHEModelDev, FHEModelClient, FHEModelServer
import numpy as np
import torch.nn as nn
from collections import Counter
import re
import pandas as pd
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
import os
import shutil
from nltk.stem.porter import PorterStemmer

REGEX = re.compile('[^a-zA-Z ]')
NUM_CATEGORIES = 5
KEYWORDS_PER_CATEGORY = 11
KEYWORDS = ['sports', 'fitness', 'athletics', 'training', 'running', 'gear', 'gym', 'exercise', 'sportswear', 'outdoors', 'wellness',
              'food', 'cuisine', 'gourmet', 'organic', 'recipes', 'delivery', 'dining', 'snacks', 'cooking', 'restaurants', 'healthy',
              'music', 'concerts', 'streaming', 'instruments', 'bands', 'festivals', 'songs', 'albums', 'lessons', 'dj', 'sound',
              'gaming', 'consoles', 'accessories', 'esports', 'multiplayer', 'virtual', 'pc', 'development', 'merchandise', 'livestream', 'communities',
              'tv', 'dramas', 'shows', 'smart', 'reviews', 'theater', 'cable', 'series', 'reality', 'channels', 'binge']

CATEGORIES = ['sports', 'food', 'music', 'gaming', 'tv']

STEMMER = PorterStemmer()
STEMMED_KEYWORDS = list(map(STEMMER.stem, KEYWORDS))
SENTENCES_PATH = './sentences.txt'
TRAINING_DATA_PATH = './training_data.csv'

def read_file_to_array(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file]
    return lines

def process_text(text):
    global CATEGORIES
    global REGEX
    global STEMMER
    
    text = text.replace("-", " ")
    text = REGEX.sub('', text)
    text = text.lower()
    text = text.split()
    text = list(map(STEMMER.stem, text))
    
    
    freq = Counter(text)
    return [freq[category] for category in STEMMED_KEYWORDS]

def non_linear_fn(x):
    global KEYWORDS_PER_CATEGORY
    reshaped = x[:len(x) - len(x) % KEYWORDS_PER_CATEGORY].reshape(-1, KEYWORDS_PER_CATEGORY)
    return np.sum(reshaped, axis=1)


def generate_training_data(corpus):
    X = normalize(corpus, axis=1, norm='l1') 
    y = np.apply_along_axis(non_linear_fn, axis=1, arr=X)
    y = normalize(y, axis=1, norm='l1')
    
    return X, y

def save_data(X, y):
    full_array = np.hstack((X, y))
    df = pd.DataFrame(full_array, columns=KEYWORDS + CATEGORIES)
    df.to_csv(TRAINING_DATA_PATH, index=False)

print(f"Keywords is multiple of # of categories {NUM_CATEGORIES * KEYWORDS_PER_CATEGORY == len(KEYWORDS)}")
corpus = read_file_to_array(SENTENCES_PATH)
corpus_mat = np.array(list(map(process_text, corpus)))

keyword_hits = np.sum(corpus_mat, axis=1)
print("KEYWORD_HITS", Counter(keyword_hits))
# Jeremiah try generating training data and running this until you get a distribution that
# favours 1-2 keyword hits, but has at least 10 examples of everything else as well (incl no hits at all)

keyword_spread = np.sum(corpus_mat, axis=0)
reshaped_keyword_spread = keyword_spread.reshape(-1, KEYWORDS_PER_CATEGORY)
delimiter = ' | '
print("KEYWORD_SPREAD")
for row in reshaped_keyword_spread:
    print(delimiter.join(map(str, row)))
# Jeremiah try generating training data and running this until you get an even distribution across all
# keywords

category_sum = reshaped_keyword_spread.sum(axis=1)
print("CATEGORY_SUM", category_sum)

X, y = generate_training_data(corpus_mat)
save_data(X, y)
