import importlib.util
from neural_net import Population
import math
import numpy as np

import sys
sys.path.insert(0, '/home/ilan/Desktop/SmartGrid')

from utils import module_from_file, mse, add_noise, plot_datas, split_sequence, mae

"""
    Training on model data using genetic algorithm
"""

# left this here in case we need it for whatever reason
def train_on_made_data():
    # import a module using its name as a string
    m = module_from_file("Data", "data/datavis.py")

    cycles = m.cycles
    data = m.Data()

    data.randomise()

    previous_cycles = cycles

    pop = Population(40, None, 2)
    best_model = None
    pc = cycles[0][0]

    test = cycles[1][0]

    print("actual: ", pc)  

    # training
    for epoch in range(100):
        preds = []
        
        for num, model in enumerate(pop.models):
            predicted_import_costs = []
            
            for i in range(data.data_points):
                if(i == 0): input = [pc[i+2], pc[i+1]]
                elif(i == data.data_points-1): input = [pc[i-1], pc[i-2]]
                else: input = [pc[i-1], pc[i+1]]
        
                predicted_import_costs.append(model.query(input)[0][0])

            pop.fitnesses[num] = 1 / mse(pc, predicted_import_costs)
            preds.append(predicted_import_costs)

            # print(f"fitness by {num}: ", pop.fitnesses[num])  

        best_model = np.argmax(pop.fitnesses)
        print(f"Best pred: {preds[best_model]}")

        # print average mse of newest population
        print("Average MSE: ", pop.average_mse())

        # plot_datas(pc, preds[np.argmax(pop.fitnesses)])

        # init new population
        pop = Population(40, pop, 2)

    # predict
    model = pop.models[best_model]
    predicted_import_costs = []

    for i in range(data.data_points):
        if(i == 0): input = [test[i+2], test[i+1]]
        elif(i == data.data_points-1): input = [test[i-1], test[i-2]]
        else: input = [test[i-1], test[i+1]]
        
        predicted_import_costs.append(model.query(input)[0][0])

    print("Prediction vs Actual")
    plot_datas(test, predicted_import_costs)


"""
    Train a model that can predict the next values given 4 previous values in
    a sliding window
"""


def train_on_sever_data():
    m = module_from_file("server_data", "data/server_data.py")

    serve = m.server_data()
    serve.set_historical_prices()

    buy = serve.parsed_data['buy_price']
    sell = serve.parsed_data['sell_price']

    # train to predict buy prices
    """
        This splits the data in such a way that X is a set of 5 consecutive values in the list, and y is the set of 5 values 
        after that. This window then moves along by 1 each time, until we are at the end of the list
    """
    X, y = split_sequence(buy, 5, 5)

    pop = Population(1, None, 5, 5)
    best_model = None

    # training
    for epoch in range(1):
        for num, model in enumerate(pop.models):
            maes = 0
            av_fitness = 0

            for i in range(len(X)):
                pred = model.query(X[i])
                pred = [i[0] for i in pred]

                print(X[i], pred, y[i])

                maes += mae(pred, y[i])

            av_fitness = len(X) / maes

            pop.fitnesses[num] = av_fitness

        best_model = np.argmax(pop.fitnesses)
        print("Best av fitness: ", pop.fitnesses[best_model])
        pop = Population(1, pop, 5, 5)

train_on_sever_data()

