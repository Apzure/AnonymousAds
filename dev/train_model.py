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
NUM_CATEGORIES = 5
KEYWORDS_PER_CATEGORY = 11
KEYWORDS = ['sports', 'fitness', 'athletics', 'training', 'running', 'gear', 'gym', 'exercise', 'sportswear', 'outdoors', 'wellness',
              'food', 'cuisine', 'gourmet', 'organic', 'recipes', 'delivery', 'dining', 'snacks', 'cooking', 'restaurants', 'healthy',
              'music', 'concerts', 'streaming', 'instruments', 'bands', 'festivals', 'songs', 'albums', 'lessons', 'dj', 'sound',
              'gaming', 'consoles', 'accessories', 'esports', 'multiplayer', 'virtual', 'pc', 'development', 'merchandise', 'livestream', 'communities',
              'tv', 'dramas', 'shows', 'smart', 'reviews', 'theater', 'cable', 'series', 'reality', 'channels', 'binge']

# why is smart in TV here?
STEMMER = PorterStemmer()
STEMMED_KEYWORDS = list(map(STEMMER.stem, KEYWORDS))
FILE_PATH = './training_data.txt'
FHE_FILE_PATH = "./fhe_directory"
FHE_FILE_PATH_CLIENT = "./fhe_directory"
FHE_FILE_PATH_SERVER = "./fhe_directory"

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


def get_training_data(X):
    # We can vary l1 or l2 in our case prob is l1
    X = normalize(X, axis=1, norm='l1') 
    
    y = np.apply_along_axis(non_linear_fn, axis=1, arr=X)
    y = normalize(y, axis=1, norm='l1')
    return train_test_split(X, y, random_state=41, test_size=0.25) # REMOVE RANDOM STATE LATER AFTER MODEL HAS BEEN SETTLED ON

def clear_fhe_dir():
    if os.path.exists(FHE_FILE_PATH):
        for filename in os.listdir(FHE_FILE_PATH):
            file_path = os.path.join(FHE_FILE_PATH, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        print(f"Cleared the directory: {FHE_FILE_PATH}")
    else:
        os.makedirs(FHE_FILE_PATH)
        print(f"Created the directory: {FHE_FILE_PATH}")


n_inputs = len(KEYWORDS)
n_outputs = NUM_CATEGORIES
params = {
    "module__n_layers": 5,
    "module__activation_function" : nn.ReLU,
    "module__n_hidden_neurons_multiplier" : 4,
    
    "module__n_w_bits" : 4, 
    "module__n_a_bits" : 4,
    
    "max_epochs": 100,
    "verbose" : True,
    "lr" : 1e-3,
}


print(f"Keywords is multiple of # of categories {NUM_CATEGORIES * KEYWORDS_PER_CATEGORY == len(KEYWORDS)}")
corpus = read_file_to_array(FILE_PATH)
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

X_train, X_test, y_train, y_test = get_training_data(corpus_mat)

concrete_regressor = NeuralNetRegressor(**params)
concrete_regressor.fit(X_train, y_train)
y_pred = concrete_regressor.predict(X_test)

print(np.sum((y_pred - y_test) ** 2) / y_pred.shape[0])

concrete_regressor.compile(X_train)
dev = FHEModelDev(path_dir=FHE_FILE_PATH, model=concrete_regressor)

clear_fhe_dir()
dev.save()

######## FURTHER TESTING #########

text = "Food foodie food food food food food food"
processed_text = process_text(text)
X = normalize(np.array(processed_text).reshape(1, -1), axis=1, norm='l1')
print(X)
# Setup the client
client = FHEModelClient(path_dir=FHE_FILE_PATH_CLIENT)
serialized_evaluation_keys = client.get_serialized_evaluation_keys()
X_enc = client.quantize_encrypt_serialize(X)


# Setup the server
server = FHEModelServer(path_dir=FHE_FILE_PATH_SERVER)
server.load()

# Server processes the encrypted data
encrypted_result = server.run(X_enc, serialized_evaluation_keys)

# Client decrypts the result
y_enc = client.deserialize_decrypt_dequantize(encrypted_result)

print(y_enc)



