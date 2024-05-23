import numpy as np
import matplotlib.pyplot as plt
import importlib.util

"""
    Useful helper functions
"""

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

def plot_datas(a, b):
    times = [i*5 for i in range(len(a))]

    if(a): plt.plot(times, a, 'r')
    if(b): plt.plot(times, b, 'b')
    plt.show()

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module