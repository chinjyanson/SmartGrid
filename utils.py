import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import importlib.util

"""
    Useful helper functions
"""

def pad(array):
    return [0]+array+[0]

def mse(a, b):
    out = 0 
    for x, y in zip(a, b):
        out += ((x - y)**2)
    
    return out / len(b)

def mae(a, b):
    out = 0 
    for x, y in zip(a, b):
        out += abs(x - y)
    
    return out / len(b)
     
def add_noise(array):
    return [round(x + np.random.normal(0, pow(len(array), -0.5)), 2) for x in array]

def plot_datas(datas, title, ylabel):   
    times = [i*5 for i in range(60)]
    colors = cm.rainbow(np.linspace(0, 1, len(datas)))

    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel(ylabel)    
    
    for i in range(len(datas)):
        plt.plot(times, datas[i], colors[i])

    plt.show()

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# split a univariate sequence into samples
def split_sequence(sequence, x_width, y_width=1):
    X, y = list(), list()
    
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + x_width
        # check if we are beyond the sequence
        if end_ix > len(sequence)-1:
            break
          
        if(end_ix + y_width > len(sequence)):
            break
        
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:end_ix+y_width]
        X.append(seq_x)
        y.append(seq_y)
          
    return np.array(X), np.array(y)