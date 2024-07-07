# This trains and compiles the model into a folder
from concrete.ml.sklearn import NeuralNetRegressor
from concrete.ml.deployment import FHEModelDev, FHEModelClient, FHEModelServer
import numpy as np
import pandas as pd
import torch.nn as nn
from collections import Counter
import re
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
import os
import shutil
from nltk.stem.porter import PorterStemmer
from generate_data import KEYWORDS, NUM_CATEGORIES , process_text

NUM_CATEGORIES = NUM_CATEGORIES
NUM_KEYWORDS = len(KEYWORDS)


FHE_FILE_PATH = "./fhe_directory"
FHE_FILE_PATH_CLIENT = "./fhe_directory"
FHE_FILE_PATH_SERVER = "./fhe_directory"
TRAINING_DATA_PATH = './training_data.csv'

df = pd.read_csv(TRAINING_DATA_PATH)
column_labels = df.columns.tolist()

KEYWORDS = column_labels[:-NUM_CATEGORIES]
CATEGORIES = column_labels[-NUM_CATEGORIES:]
X = df.values[:, :-NUM_CATEGORIES]
y = df.values[:, -NUM_CATEGORIES:]

print(X.shape, y.shape)

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


n_inputs = NUM_KEYWORDS
n_outputs = NUM_CATEGORIES
params = {
    "module__n_layers": 3,
    "module__activation_function" : nn.ReLU,
    "module__n_hidden_neurons_multiplier" : 4,
    
    "module__n_w_bits" : 4, 
    "module__n_a_bits" : 4,
    
    "max_epochs": 150,
    "verbose" : True,
    "lr" : 1e-3,
}







X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25) 

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



