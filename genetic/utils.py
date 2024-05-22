import numpy as np

def pad(array):
    return [0]+array+[0]

def mse(actual, pred):
    out = 0 
    for x, y in zip(actual, pred):
        out += ((x - y)**2)
    
    return out / len(actual)

def add_noise(array):
    m = np.mean(array)

    return [x + np.random.normal(m, pow(m.size, -0.5)) for x in array]