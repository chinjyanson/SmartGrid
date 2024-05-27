import importlib.util
from neural_net import Population, neural_net
import math
import numpy as np
from helper import module_from_file, mse, plot_datas, save_population, get_population, add_noise

# class Import:
#     def __init__(self):
#         self.Population = Population()
#         self.neural_net = neural_net()


import sys
sys.path.insert(0, '/Users/ASUS/SmartGrid')

# def import_helper():
#     module_from_file()
#     mse()
#     plot_datas()
#     save_population()
#     get_population()
#     add_noise()

#from utils.helper import module_from_file, mse, plot_datas, save_population, get_population, add_noise

m_server = module_from_file("server_data", "buy-sell-algorithm/data/server_data.py")
m_made = module_from_file("Data", "buy-sell-algorithm/data/datavis.py")

serve = m_server.server_data()

class Train:
    """
        Train models using a genetic algorithm to synthesize data if needed, and predict data in a cycle
    """
    call_counter = 0

    def __init__(self) -> None:
        # save up to 5 histories of data required for prediction of each  form of data
        self.histories_buffer = {'buy_price':[], 'sell_price':[], 'demand':[]}
        self.data_fitnesses = {'buy_price':0, 'sell_price':0, 'demand':0}
        self.num_of_histories = 5
        self.fitness_threshold = 0
        self.fitness_buffer = []
        self.epsilon = 0.0001
        self.save_checkpoint = 1
        self.saved_pop_path = os.path.join(train_root, "saved_populations")

        os.makedirs(self.saved_pop_path, exist_ok=True)

    def train_on_made_data(self) -> None:
        """
            This is no longer in use, but left here for testing if needed
        """
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

    def get_synthetic_data(self, data_type : str, num_of_available_histories : int) -> tuple[list[list], list]:
        """
            return a tuple of actual data and a set of synthetic data derived from this actual data
        """
        serve.set_historical_prices()
        h_data = serve.parsed_data[data_type]

        print("Training to synthesize similar data from one previous cycle")

        out = []
        amount = min(self.num_of_histories - num_of_available_histories, 10)

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

            pop = Population(10, pop, 2)
        
        return out, h_data
    
    def asymptotic(self, fitness:float) -> bool:
        """
            Need to flesh out this idea
        """
        if(len(self.fitness_buffer) >= 5):
            self.fitness_buffer = []
            return all([abs(fitness - i) <= self.epsilon for i in self.fitness_buffer])
        
        return False

    def train_on_histories(self, histories : list[list], most_recent:list):
        """
            given a set of histories, and the most recent history, train to predict the cycle of the 
            most recent history
        """
        print("Training on the historical data. Training to predict most recent cycle")
        print("Threshold: ", self.fitness_threshold)

        old_pop = get_population(self.saved_pop_path)

        if(old_pop):
            pop = Population(50, old_pop, self.num_of_histories, 6, 6)
            print("Loaded previous best population")
        else:
            pop = Population(50, None, self.num_of_histories, 6, 6)
            print("Started from random population")

        best_pred = None
        best_fitness = None
        most_recent_pop = None

        for epoch in range(80):
            print("Epoch: ", epoch+1)
            preds = []

            for num, model in enumerate(pop.models):
                prediction = []

                for j in range(60):
                    input = []
                    for i in range(self.num_of_histories):
                        input.append(histories[i][j])   

                    prediction.append(model.query(input)[0][0])

                pop.fitnesses[num] = 1 / mse(most_recent, prediction)
                preds.append(prediction)

            best_model_index = np.argmax(pop.fitnesses)
            best_pred = preds[best_model_index]
            best_fitness = pop.fitnesses[best_model_index]

            if ((self.fitness_threshold != 0) and (best_fitness > self.fitness_threshold)):
                break
            else:
                self.fitness_buffer.append(best_fitness)
            
            # plot_datas([best_pred, most_recent], "Training to predict most recent cycle given histories", "Data")
            print("Best fitness: ", best_fitness)

            most_recent_pop = pop
            pop = Population(50, pop, self.num_of_histories, 6, 6)
        
        plot_datas([best_pred, most_recent], "Best prediction of most recent cycle", "Data")

        # save the best population when this is called. when this function gets called again, it will start from this population of genomes instead of starting randomly
        # save based on a checkpoint, saves every time this function is called by default
        if((Train.call_counter % self.save_checkpoint) == 0):
            save_population(most_recent_pop, self.saved_pop_path)

        return pop.models[best_model_index], best_fitness

    def query_model(self, data : str) -> list[int] | None:
        """
        - this should be called at the beginning of each cycle to predict values for whole cycle
        - it takes some time:
        * the very first time this is called, the histories buffer will be empty, so it has to synthesize it own for prediction training, which is an extra overhead.
        
        Return prediction of next cycle
        """

        if(data in self.histories_buffer):
            available_histories = self.histories_buffer[data]

            if(len(available_histories) < self.num_of_histories):
                print(f"Not enough histories for {data}, need to synthesize 5 histories for training")
                previous, most_recent = self.get_synthetic_data(data, len(available_histories))
                self.histories_buffer[data] = previous[1:]
                self.histories_buffer[data].append(most_recent)
            else:
                print(f"Have 5 histories for {data}, get most recent data for training")
                serve.set_historical_prices()
                previous, most_recent = available_histories, serve.parsed_data[data]
                # discard the least recent history, append most recent history, always keep availability of 5
                self.histories_buffer[data] = self.histories_buffer[data][1:]
                self.histories_buffer[data].append(most_recent)  # discard the least recent history, append most recent history, always keep availability of 5
            
            if(self.data_fitnesses[data] != 0): self.fitness_threshold = min(add_noise(self.data_fitnesses[data]), 1)

            # train model to predict the most recent cycle given a set of previous cycles
            best_model, best_fitness = self.train_on_histories(previous, most_recent)

            self.data_fitnesses[data] = best_fitness

            prediction = []
            for j in range(60):
                input = []
                for i in range(self.num_of_histories):
                    input.append(self.histories_buffer[data][i][j])   

                prediction.append(best_model.query(input)[0][0])

            return prediction

        else:
            print("Training on this data not implemented yet")
            return None
        
if __name__ == "__main__":
    trainer = Train()

    buy = trainer.query_model('buy_price')
    plot_datas([buy], "Prediction of current cycle", "Buy price")

    sell = trainer.query_model('sell_price')
    plot_datas([sell], "Prediction of current cycle", "Sell price")

    sell = trainer.query_model('sell_price')
    plot_datas([sell], "Prediction of current cycle", "Sell price")