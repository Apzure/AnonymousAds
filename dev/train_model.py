# This trains and compiles the model into a folder
from concrete.ml.sklearn import NeuralNetRegressor
from concrete.ml.deployment import FHEModelDev, FHEModelClient, FHEModelServer
import numpy as np
import torch.nn as nn
from collections import Counter
import re
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
import os
import shutil
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
FILE_PATH = './training_data.txt'
FHE_FILE_PATH = "./fhe_directory"
FHE_FILE_PATH_CLIENT = "./client"
FHE_FILE_PATH_SERVER = "./server"

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

def non_linear_fn(x):
    # current model for testing
    global KEYWORDS_PER_CATEGORY
    reshaped = x[:len(x) - len(x) % KEYWORDS_PER_CATEGORY].reshape(-1, KEYWORDS_PER_CATEGORY)
    sums = np.sum(reshaped, axis=1)
    return sums

def get_training_data(X):
    # We can vary l1 or l2 in our case prob is l1
    X = normalize(X, axis=1, norm='l1') 
    
    y = np.apply_along_axis(non_linear_fn, axis=1, arr=X)
    y = normalize(y, axis=1, norm='l1')
    
    return train_test_split(X, y, random_state=41, test_size=0.25) # REMOVE RANDOM STATE LATER AFTER MODEL HAS BEEN SETTLED ON

def clear_fhe_dir():
    if os.path.exists(FHE_FILE_PATH):
        shutil.rmtree(FHE_FILE_PATH)
        print(f"Removed the directory: {FHE_FILE_PATH}")
    os.makedirs(FHE_FILE_PATH)
    print(f"Created the directory: {FHE_FILE_PATH}")


n_inputs = 50
n_outputs = 5
params = {
    "module__n_layers": 3,
    "module__activation_function" : nn.ReLU,
    "module__n_hidden_neurons_multiplier" : 4,
    
    "module__n_w_bits" : 3, 
    "module__n_a_bits" : 3,
    "module__n_accum_bits" : 64,
    
    "max_epochs": 10,
    "verbose" : True,
    "lr" : 1e-3,
}


print(f"Keywords is multiple of # of categories {len(CATEGORIES) % KEYWORDS_PER_CATEGORY == 0}")
corpus = read_file_to_array(FILE_PATH)
corpus_mat = np.array(list(map(process_text, corpus)))

keyword_hits = np.sum(corpus_mat, axis=1)
print("KEYWORD_HITS", Counter(keyword_hits))
# Jeremiah try generating training data and running this until you get a distribution that
# favours 1-2 keyword hits, but has at least 10 examples of everything else as well (incl no hits at all)

keyword_spread = np.sum(corpus_mat, axis=0)
print("KEYWORD_SPREAD", keyword_spread)
# Jeremiah try generating training data and running this until you get an even distribution across all
# keywords

X_train, X_test, y_train, y_test = get_training_data(corpus_mat)

concrete_regressor = NeuralNetRegressor(**params)
concrete_regressor.fit(X_train, y_train)
y_pred = concrete_regressor.predict(X_test)

print(np.sum((y_pred - y_test) ** 2) / y_pred.shape[0])

concrete_regressor.compile(X_train)
dev = FHEModelDev(path_dir=FHE_FILE_PATH, model=concrete_regressor)

clear_fhe_dir()
dev.save()


# Setup the client
client = FHEModelClient(path_dir=FHE_FILE_PATH_CLIENT, key_dir="/tmp/keys_client")
serialized_evaluation_keys = client.get_serialized_evaluation_keys()
X_enc = client.quantize_encrypt_serialize(X_test)

X_new = np.random.rand(1, 20)
encrypted_data = client.quantize_encrypt_serialize(X_new)

# Setup the server
server = FHEModelServer(path_dir=FHE_FILE_PATH_SERVER)
server.load()

# Server processes the encrypted data
encrypted_result = server.run(encrypted_data, serialized_evaluation_keys)

# Client decrypts the result
y_enc = client.deserialize_decrypt_dequantize(encrypted_result)

print("ENCRYPTED LOSS", np.sum((y_enc - y_test) ** 2) / y_test.shape[0])