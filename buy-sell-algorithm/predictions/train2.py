import sys, os

train_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))

if train_root not in sys.path:
    sys.path.insert(0, train_root)

from neural_net import Population, neural_net
import numpy as np
from utils.helper import module_from_file, mse, plot_datas, save_population, get_population, add_noise
from multiprocessing import Process
import time

def print_num():
    for i in range(6):
        print(i)

def print_letter():
    for i in ['a','b','c','d','e','f']:
        print(i)

start = time.time()

#print_num()
#print_letter()

p1 = Process(target=print_num)
p2 = Process(target=print_letter)

p1.start()
p2.start()

p1.join()
p2.join()

print(time.time()-start)