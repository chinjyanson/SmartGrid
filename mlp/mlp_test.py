"""
    Testing with Multi-layer Perceptron models from keras library
"""

from numpy import array

import sys
sys.path.insert(0, '/home/ilan/Desktop/SmartGrid')

from utils import module_from_file, split_sequence
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
import numpy as np

from sklearn.model_selection import train_test_split, KFold

# import a module using its name as a string
m = module_from_file("Data", "data/datavis.py")

cycles = m.cycles
data = m.Data()
data.randomise()

previous_imports = cycles[0][0]


# choose a number of time steps
n_steps = 4
X, y = split_sequence(previous_imports, n_steps)

# X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)


# Number of folds
k = 5
kf = KFold(n_splits=k, shuffle=True, random_state=42)

val_mae_per_fold = []

X_val, y_val = [], []

for train_index, val_index in kf.split(X):
    # Split data
    X_train, X_val = X[train_index], X[val_index]
    y_train, y_val = y[train_index], y[val_index]
	
    model = Sequential()
    model.add(Dense(64, input_dim=4, activation='relu'))  # First hidden layer with 64 units
    model.add(Dense(32, activation='relu'))               # Second hidden layer with 32 units
    model.add(Dense(1, activation='linear'))              # Output layer with 1 unit

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    history = model.fit(X_train, y_train, epochs=100, batch_size=10, validation_data=(X_val, y_val))

    for i in range(len(X_val)):
        print(X_val[i], y_val[i])

    # Evaluate the model
    loss, mae = model.evaluate(X_val, y_val, verbose=0)
    val_mae_per_fold.append(mae)
	
average_mae = np.mean(val_mae_per_fold)
print("Average mae: ", average_mae)

# Make predictions
predictions = model.predict(X_val)
for i in range(len(X_val)):
	print(X_val[i], predictions[i])