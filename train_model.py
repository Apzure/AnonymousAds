# This trains and compiles the model into a folder
from concrete.ml.sklearn import DecisionTreeClassifier
from concrete.ml.deployment import FHEModelDev, FHEModelClient, FHEModelServer
import numpy as np

# Define the directory for FHE client/server files
fhe_directory = '/tmp/fhe_client_server_files/'

# Initialize the Decision Tree model
model = DecisionTreeClassifier()

print("IMPORTED MODEL")
# Generate some random data for training
X = np.random.rand(100, 20)
y = np.random.randint(0, 2, size=100)

# Train and compile the model
model.fit(X, y)
model.compile(X)

print("COMPILED MODEL")
# Setup the development environment
dev = FHEModelDev(path_dir=fhe_directory, model=model)
dev.save()

print("SAVED MODEL")
# Setup the client
client = FHEModelClient(path_dir=fhe_directory, key_dir="/tmp/keys_client")
serialized_evaluation_keys = client.get_serialized_evaluation_keys()

print(serialized_evaluation_keys)

# Client pre-processes new data
X_new = np.random.rand(1, 20)
encrypted_data = client.quantize_encrypt_serialize(X_new)

# Setup the server
server = FHEModelServer(path_dir=fhe_directory)
server.load()

# Server processes the encrypted data
encrypted_result = server.run(encrypted_data, serialized_evaluation_keys)

# Client decrypts the result
result = client.deserialize_decrypt_dequantize(encrypted_result)