import importlib.util
from neural_net import Population
import math
from utils import pad, mse, add_noise

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# import a module using its name as a string
m = module_from_file("Data", "data/datavis.py")

cycles = m.cycles
data = m.Data()

data.randomise()

previous_cycles = cycles

pop = Population(10, None, 3)
prev_cycle = cycles[0]

for epoch in range(1000):
    import_costs = [round(x) for x in prev_cycle[0]]
    irradiance = [round(x) for x in prev_cycle[1]]

    for num, model in enumerate(pop.models):
        predicted_import_costs = []
        
        for i in range(data.data_points):
            if (i == 0): 
                input = [irradiance[i], 0, import_costs[1]]
            elif(i == data.data_points-1):
                input = [irradiance[i], import_costs[i-1], 0]
            else:
                input = [irradiance[i], import_costs[i-1], import_costs[i+1]]

            predicted_import_costs.append(model.query(input)[0][0])

        pop.fitnesses[num] = 1 / mse(import_costs, predicted_import_costs)

    # print average mse of newest population
    print("Average MSE: ", pop.average_mse())

    # init new population
    pop = Population(10, pop, 3)

    import_costs = add_noise(import_costs)
    irradiance = add_noise(irradiance)
            
