import importlib.util
from neural_net import Population
import math
import numpy as np

import sys
sys.path.insert(0, '/Users/ASUS/SmartGrid')

from utils import module_from_file, mse, add_noise, plot_datas, split_sequence, mae

m_server = module_from_file("server_data", "data/server_data.py")
m_made = module_from_file("Data", "data/datavis.py")

serve = m_server.server_data()

histories_buffer = {'buy_price':[], 'sell_price':[], 'demand':[]}

"""
    Training on model data using genetic algorithm
"""

# left this here in case we need it for whatever reason
def train_on_made_data():
    cycles = m_made.cycles
    data = m_made.Data()
    data.randomise()

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

        # init new population
        pop = Population(40, pop, 2)

    # predict
    model = pop.models[best_model]
    predicted_import_costs = []

    for i in range(data.data_points):
        if(i == 0): input = [test[i+2], test[i+1]]
        elif(i == data.data_points-1): input = [test[i-1], test[i-2]]
        else: input = [test[i-1], test[i+1]]   

    print("Prediction vs Actual")

"""
    return a tuple of actual data and a set of synthetic data derived from this actual data
"""
def get_synthetic_data(data_type, amount):
    serve.set_historical_prices()
    h_data = serve.parsed_data[data_type]

    print("Training to synthesize similar data from one previous cycle")

    out = []
    amount = min(amount, 10)

    pop = Population(10, None, 2)
    best_model = None
    data_points = 60

    # training
    for epoch in range(50):
        preds = []
        
        for num, model in enumerate(pop.models):
            predicted_import_costs = []
            
            for i in range(data_points):
                if(i == 0): input = [h_data[i+2], h_data[i+1]]
                elif(i == data_points-1): input = [h_data[i-1], h_data[i-2]]
                else: input = [h_data[i-1], h_data[i+1]]
        
                predicted_import_costs.append(model.query(input)[0][0])

            pop.fitnesses[num] = 1 / mse(h_data, predicted_import_costs)
            preds.append(predicted_import_costs)

        best_model = np.argmax(pop.fitnesses)
        
        if(not(epoch % 10) and len(out) < amount):
            out.append(preds[best_model])

        # plot_datas([h_data, preds[best_model]], "Synthetic data vs Actual data", data_type)

        pop = Population(10, pop, 2)
    
    return out, h_data


num_of_histories = 5

# train on a set of historical datas
def train_on_histories(histories, most_recent):
    """
        given a set of histories, and the most recent history, train to predict the cycle of the 
        most recent history
    """
    print("Training on the historical data. Training to predict most recent cycle")

    pop = Population(100, None, num_of_histories)
    best_pred = None

    for epoch in range(100):
        preds = []

        for num, model in enumerate(pop.models):
            prediction = []

            for j in range(60):
                input = []
                for i in range(num_of_histories):
                    input.append(histories[i][j])   

                prediction.append(model.query(input)[0][0])

            pop.fitnesses[num] = 1 / mae(most_recent, prediction)
            preds.append(prediction)

        best_model_index = np.argmax(pop.fitnesses)
        best_pred = preds[best_model_index]

        # plot_datas([best_pred, actual], "Training to predict most recent cycle given histories", "Data")

        # print("Best fitness: ", pop.fitnesses[best_model_index])

        pop = Population(100, pop, num_of_histories)

    #plot_datas([best_pred, most_recent], "Best prediction of most recent cycle", "Data")

    return pop.models[best_model_index]

"""
    - this should be called at the beginning of each cycle to predict values for whole cycle
    - it takes some time:
    * the very first time this is called, the histories buffer will be empty, so it has to synthesize it own for prediction training, which is an extra overhead.
    I've made it such that this is needed only once, so at future calls, this overhead is removed. With overhead: 1min, without: 30 secs

"""

def query_model(data):
    if(data in histories_buffer):
        available_histories = histories_buffer[data]

        if(len(available_histories) < num_of_histories):
            previous, most_recent = get_synthetic_data(data, num_of_histories-len(available_histories))
            histories_buffer[data] = previous[1:]
            histories_buffer[data].append(most_recent)
        else:
            previous, most_recent = available_histories, serve.parsed_data[data]
            # discard the least recent history, append most recent history, always keep availability of 5
            histories_buffer[data] = histories_buffer[data][1:]
            histories_buffer[data].append(most_recent)  # discard the least recent history, append most recent history, always keep availability of 5

        # train model to predict the most recent cycle given a set of previous cycles
        best_model = train_on_histories(previous, most_recent)

        prediction = []
        for j in range(60):
            input = []
            for i in range(num_of_histories):
                input.append(histories_buffer[data][i][j])   

            prediction.append(best_model.query(input)[0][0])

        #plot_datas([prediction], "Prediction of current cycle", data)
        print(prediction)

        return prediction

    else:
        print("Training on this data not implemented yet")
        return None

if __name__ == "__main__":
    query_model('sell_price')
