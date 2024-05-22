import numpy as np
import random
import math
import matplotlib.pyplot as plt

# data for 10 cycles
cycles = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]}

cycle_time = 300  # 5 minutes
random_time = 5   # 5 seconds for new random data

data_points = cycle_time // random_time

import_costs = []
export_costs = []
irradiance_vals = []

sines = [np.sin(((i+1)/30)*math.pi) for i in range(data_points)]

# randomise array with 60 random values to simulate a day / cycle
# spec says there's a repeating periodic component as well, so I have got my values from sin graph
def randomise(input_arrays):    
    for a in input_arrays:
        a.clear()
        for i in range(data_points):
            a.append(round(random.randrange(0, 101, 2) + 10*sines[i], 2))

# 0 = import, 1 = export, 2 = irrandiance
def populate_data():
    for num, _ in cycles.items():
        randomise([import_costs, export_costs, irradiance_vals])
        cycles[num] = [import_costs, export_costs, irradiance_vals]

def print_data():
    for cycle in cycles.values():
        print(cycle)

def plot_data(data_index):
    times = [i*5 for i in range(data_points)]
    figure, axis = plt.subplots(2, len(cycles) // 2)

    for row in range(2):
        for col in range(len(cycles) // 2):
            cycle_num = 5*row + col
            axis[row, col].plot(times, cycles[cycle_num][data_index])
            axis[row, col].set_title(f"Cycle number {cycle_num}")
        
    plt.show()

populate_data()
print_data()
plot_data(0)