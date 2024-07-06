# This trains and compiles the model into a folder
from concrete.ml.sklearn import NeuralNetRegressor
from concrete.ml.deployment import FHEModelDev, FHEModelClient, FHEModelServer
import numpy as np
import torch.nn as nn
from collections import Counter
import re
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split

from nltk.stem.porter import PorterStemmer

REGEX = re.compile('[^a-zA-Z ]')
KEYWORDS_PER_CATEGORY = 10
CATEGORIES = ['fitness', 'athletics', 'training', 'running', 'gear', 'gym', 'exercise', 'sportswear', 'outdoors', 'wellness',
              'cuisine', 'gourmet', 'organic', 'recipes', 'delivery', 'dining', 'snacks', 'cooking', 'restaurants', 'healthy',
              'concerts', 'streaming', 'instruments', 'bands', 'festivals', 'songs', 'albums', 'lessons', 'dj', 'sound',
              'consoles', 'accessories', 'esports', 'multiplayer', 'virtual', 'pc', 'development', 'merchandise', 'streaming', 'communities',
              'streaming', 'shows', 'smart', 'reviews', 'theater', 'cable', 'series', 'reality', 'channels', 'binge']

# why is smart in TV here? also rename Categories to keywords
STEMMER = PorterStemmer()
STEMMED_CATEGORIES = list(map(STEMMER.stem, CATEGORIES))

print(f"Keywords is multiple of # of categories {CATEGORIES % KEYWORDS_PER_CATEGORY == 0}")

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
    vector = [freq[category] for category in STEMMED_CATEGORIES]
    return vector

file_path = 'training_data.txt'
corpus = read_file_to_array(file_path)
corpus_mat = np.array(list(map(process_text, corpus)))

keyword_hits = np.sum(corpus_mat, axis=1)
print("KEYWORD_HITS", Counter(keyword_hits))

# Jeremiah try generating training data and running this until you get a distribution that
# favours 1-2 keyword hits, but has at least 10 examples of everything else as well (incl no hits at all)

keyword_spread = np.sum(corpus_mat, axis=0)
print("KEYWORD_SPREAD", keyword_spread)

# Jeremiah try generating training data and running this until you get an even distribution across all
# keywords

normalised_data = normalize(corpus_mat, axis=1, norm='l1') #We can vary l1 or l2 in our case prob is l1

def non_linear_fn(x):
    # current model for testing
    global KEYWORDS_PER_CATEGORY
    print(f"SHAPE OF X is CORRECT {x.shape[0] % KEYWORDS_PER_CATEGORY == 0}")
    reshaped = x[:len(x) - len(x) % KEYWORDS_PER_CATEGORY].reshape(-1, KEYWORDS_PER_CATEGORY)
    sums = np.sum(reshaped, axis=1)
    return sums

def get_training_data(X):
    y = np.apply_along_axis(non_linear_fn, axis=1)
    return train_test_split(X, y, random_state=41, test_size=0.25) # REMOVE RANDOM STATE LATER AFTER MODEL HAS BEEN SETTLED ON

n_inputs = 50
n_outputs = 5
params = {
    "module__n_layers": 3,
    "module__activation_function" : nn.ReLU,
    "module__n_hidden_neurons_multiplier" : 4,
    
    "n_w_bits" : 3, 
    "n_a_bits" : 3,
    "n_accum_bits" : 64,
    
    "max_epochs": 3,
    "verbose" : True,
    "lr" : 1e-3,
}

concrete_classifier = NeuralNetRegressor(**params)
get_training_data(X)

