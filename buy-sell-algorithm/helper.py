import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import importlib.util
import pickle


"""
    Useful helper functions
"""

def pad(array):
    return [0]+array+[0]

def mse(a, b):
    """
        Mean squared error
    """
    out = 0 
    for x, y in zip(a, b):
        out += ((x - y)**2)
    
    return out / len(b)

def sse(a, b):
    """
        Sum of squared errors
    """
    out = 0 
    for x, y in zip(a, b):
        out += (x - y)**2
                
    return out

def mae(a, b):
    """
        Mean absolute error
    """
    out = 0 
    for x, y in zip(a, b):
        out += abs(x - y)
    
    return out / len(b)
     
def add_noise(x):
    return 5*x

def plot_datas(datas, title, ylabel):   
    """
    Pass a list of datas to plot
    set of data on the same graph needs to be put into a list
    """

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

def save_population(pop):
    try:
        with open("best.pop", "wb") as f:
            pickle.dump(pop, f)
    except IOError as e:
        print("Could not save population because of ", e)

def get_population():
    try:
        with open("best.pop", "rb") as f:
            return pickle.load(f)
    except IOError as e:
        print("Could not load population because of ", e)
