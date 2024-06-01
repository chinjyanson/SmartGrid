import sys, os

train_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))

if train_root not in sys.path:
    sys.path.insert(0, train_root)

from neural_net import Population, neural_net
import numpy as np
from utils.helper import module_from_file, mse, plot_datas, save_population, get_population, add_noise, batch_up
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import time
import asyncio
from threading import Thread
from threading import current_thread

m_server = module_from_file("server_data", "buy-sell-algorithm/data/server_data.py")
m_made = module_from_file("Data", "buy-sell-algorithm/data/datavis.py")

serve = m_server.server_data()

class Train:
    """
        Train models using a genetic algorithm to synthesize data if needed, and predict data in a cycle
    """

    def __init__(self, elitism, mutation_prob, mutation_power, max_epochs, num_of_histories, data_batch_size, nn_batch_size, parsed_data) -> None:
        self.histories_buffer = {'buy_price':[], 'sell_price':[], 'demand':[]}
        self.data_fitnesses = {'buy_price':0, 'sell_price':0, 'demand':0}
        self.num_of_histories = num_of_histories
        self.fitness_threshold = 0
        self.fitness_buffer = []
        self.epsilon = 0.0001
        self.save_checkpoint = 1
        self.saved_pop_path = os.path.join(train_root, "saved_populations")

        self.elitism = elitism
        self.mutation_prob = mutation_prob
        self.mutation_power = mutation_power

        self.epochs = max_epochs

        self.data_batch_size = data_batch_size
        self.nn_batch_size = nn_batch_size

        self.parsed_data = parsed_data

        os.makedirs(self.saved_pop_path, exist_ok=True)

    def change_historical_data(self, hd):
        self.parsed_data = hd

    def first_call(self) -> bool:
        return any([b==[] for b in self.histories_buffer.values()])

    def get_synthetic_data(self, data_type : str) -> tuple[list[list], list]:
        """
            return a tuple of actual data and a set of synthetic data derived from this actual data
        """
        h_data = self.parsed_data[data_type]

        print("Training to synthesize similar data from one previous cycle")

        out = []
        amount = min(self.num_of_histories, 10)

        pop = Population(2, pop_size=5, input_nodes=2, output_nodes=1, mutation_prob=self.mutation_prob, mutation_power=self.mutation_power, elitism=self.elitism)
        best_model = None
        data_points = 60
        epochs = 20
        checkpoints = list(map(lambda x : (x[0]+x[1]) // 2, batch_up((0,epochs), epochs//self.num_of_histories)))
        check_counter = 0

        # training
        for epoch in range(epochs):
            synthetics = []
            
            for model in pop.models:
                synth = []
                
                for i in range(data_points):
                    if(i == 0): input = [h_data[i+2], h_data[i+1]]
                    elif(i == data_points-1): input = [h_data[i-1], h_data[i-2]]
                    else: input = [h_data[i-1], h_data[i+1]]
            
                    synth.append(model.query(input)[0][0])

                pop.fitnesses.append(1 / mse(h_data, synth))
                synthetics.append(synth)

            best_model = np.argmax(pop.fitnesses)
        
        
            if(check_counter < self.num_of_histories and checkpoints[check_counter] == epoch):
                out.append(synthetics[best_model])
                check_counter += 1


            pop = Population(old_pop=pop)
        
        return out, h_data
    
    def make_prediction(self, start_index, end_index, model, histories):
        prediction = []

        for j in range(start_index, end_index):
            input = []
            for i in range(self.num_of_histories):
                try:
                    input.append(histories[i][j])
                except IndexError as e:
                    print(histories, i, j)
                    print(e)
                    sys.exit(1)  

            prediction.append(model.query(input)[0][0])

        return prediction
        
    def train_models(self, models : neural_net, histories : list[list[float]], most_recent : list[float], start_index : int, end_index : int) -> tuple[list[float], list[float]]:
        """
            Train models on a set of histories and return a tuple lists of each model's fitness, and each model's prediction 
        """
        fitnesses = []
        predictions = []

        for model in models:
            # run different copies of the model in parallel on different batches of the histories to make predictions
            # full range is 0->60, make in batches of 15

            #batches = batch_up((0, 60), self.data_batch_size)
            prediction = []

            #for batch in batches:
            #   prediction += self.make_prediction(*batch, model, histories)

            prediction = self.make_prediction(start_index, end_index, model, histories)
            predictions.append(prediction)
            
            fitnesses.append(1 / mse(most_recent, prediction))

        return fitnesses, prediction
    
    def train_on_histories(self, histories : list[list[float]], most_recent : list[float], data : str, start_index : int, end_index : int) -> neural_net:
        """
            given a set of histories, and the most recent history, train to predict the cycle of the 
            most recent history
        """
        best_pred = None
        best_fitness = None
        most_recent_pop = None

        file_name = os.path.join(self.saved_pop_path, data+".pop")
        old_pop = get_population(file_name)

        if(old_pop):
            pop = Population(old_pop=old_pop)
            print("Loaded previous best population")
        else:
            pop = Population(6, pop_size=50, input_nodes=self.num_of_histories, output_nodes=1, mutation_prob=self.mutation_prob, 
                            elitism=self.elitism, mutation_power=self.mutation_power)
            
            print("Started from random population")

        for epoch in range(self.epochs):
            print("Epoch: ", epoch+1)

            fitnesses, predictions = self.train_models(pop.models, histories, most_recent, start_index, end_index)
            pop.fitnesses = fitnesses

            best_model_index = np.argmax(pop.fitnesses)
            # best_pred = all_predictions[best_model_index]
            best_fitness = pop.fitnesses[best_model_index]

            if ((self.fitness_threshold != 0) and (best_fitness > self.fitness_threshold)):
                break
            else:
                self.fitness_buffer.append(best_fitness)
            
            print("Best fitness: ", best_fitness)

            most_recent_pop = pop
            pop = Population(old_pop=pop)
        
        save_population(most_recent_pop, file_name)   

        self.data_fitnesses[data] = best_fitness

        return pop.models[best_model_index]

    def query_model(self, data_name : str, start_index : int, end_index:int, most_recent : list[float]) -> list[int] | None:
        """
        - this should be called at the beginning of each cycle to predict values for whole cycle
        - it takes some time:
        - the very first time this is called, the histories buffer will be empty, so it has to synthesize it own for prediction training, which is an extra overhead.
        - Prediction returned will only be between `start_index` and `end_index`
        - Return prediction of next cycle
        """
        print()
        if(data_name in self.histories_buffer):
            previous = self.histories_buffer[data_name] #self.parsed_data[data_name]

            #if(start_index == 0):
            #    self.histories_buffer[data_name] = previous[1:] + [most_recent]
            #else:
            #    self.histories_buffer[data_name][-1] += most_recent
            
            if(self.data_fitnesses[data_name] != 0): self.fitness_threshold = min(add_noise(self.data_fitnesses[data_name], 2), 100)

            print("Training on the historical data. Training to predict most recent cycle")
            print("Threshold: ", self.fitness_threshold)

            # train model to predict the most recent cycle given a set of previous cycles
            best_model = self.train_on_histories(previous, most_recent, data_name, start_index, end_index)

            prediction = []
            for j in range(start_index, end_index):
                input = []
                for i in range(self.num_of_histories):
                    input.append(self.histories_buffer[data_name][i][j])   

                prediction.append(best_model.query(input)[0][0])

            return prediction

        else:
            print("Training on this data not implemented yet")
            return None
        
if __name__ == "__main__":
    """
        This setup tries to show how the trainer should be used.

        The flow: 
            - At tick = 0, get historical data. If this is first call to trainer, set predictions to most recent history. If not, set
            predictions to already prepared next predictions 
            - At every 15th tick, fill up next predictions buffers using a batch of 15 values stored in the live datas buffers
            - At every other tick, do something else, including filling up data buffers

        This assumes that the server tick is also at 0, here: `cycles = sum([[i for i in range(60)] for _ in range(3)], [])`. When the trainer gets 
        called for the first time. So it should be the case that  if the live tick isn't at 0 yet, just uses the historical data as the prediction 
        for the next cycle.

        Just so I can plot nice graphs without having to wait for 5 minutes for each cycle, and show the training speed, I've commented out the
        functions that get the live data, and used the most recent history to train the models for next predictions here: 
        `next_predictions[data_name] += trainer.query_model(data_name, x, y, serve.parsed_data[data_name][x:y])`

        In reality, we want to use the live buffers for training, and update them at the relevant time steps
    """

    trainer = Train(elitism=0.2, mutation_prob=0.08, mutation_power=0.1, max_epochs=20, num_of_histories=5, 
                data_batch_size=15, nn_batch_size=60, parsed_data=serve.parsed_data)
    loop = asyncio.get_event_loop()
    
    def new_cycle(data_buffers, predictions, next_predictions):
        """
            - Set prediction of current cycle to be the most recent history if this is first call to trainer at tick 0
            - If this is not first call to trainer at tick 0, then next predictions should become current predictions
            - Empty data and next predictions buffers, add current values into data buffers to begin with
        """
        start = time.time()

        # at start of new cycle, prepare predictions for current cycle, and set correct historical data
        serve.set_historical_prices()
        trainer.change_historical_data(serve.parsed_data)

        if(trainer.first_call()):
            print("First call, assume predictions for all data is most recent cycle")
            
            for data_name, _ in trainer.histories_buffer.items():
                previous, most_recent = trainer.get_synthetic_data(data_name)
                trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
                predictions[data_name] = most_recent
            
        else:
            print("Current predictions are ready")
            if any([len(n) == 0 for n in next_predictions.values()]):
                predictions = trainer.histories_buffer
            else:
                predictions = next_predictions.copy()

        # empty data and next prediction buffers and add the current live values
        serve.live_data()
        
        for data_name in ['buy_price', 'sell_price', 'demand']:
            data_buffers[data_name] = []
            next_predictions[data_name] = []
            data_buffers[data_name].append(serve.parsed_data[data_name])

        for n, p in predictions.items():
            plot_datas([p], "Prediction", n)

        return time.time() - start
    
    def prepare_next(i, starting_i, data_buffers, next_predictions):
        """
            - Prepare predictions for the next cycle using the data buffers you have so far
            - Also add value at current tick into data buffer
        """
        start = time.time()
        # prepare next predictions for next batch each time we are at tick 15, 30, 45, 60
        # start a new thread that does this batch while another thread continues on with the for loop
        
        serve.live_data()

        for data_name in ['buy_price', 'sell_price', 'demand']:
            data_buffers[data_name].append(serve.parsed_data[data_name])
        
        # if we started at new cycle, then get nexts
        # if we didn't 
        if(not ((starting_i % 15 == 0) and (trainer.first_call())) or starting_i < 30):
            if(0 < i  - starting_i < 15):
                dist = i - starting_i
            else:
                dist = 15

            if(i == 59):
                x, y = 60-dist, 60
            else:
                x, y = batch_up((i-dist, i), dist)[0]


            for data_name in ['buy_price', 'sell_price', 'demand']:
                # print(x, y, data_buffers[data_name][x:y+1])   

                if(next_predictions[data_name] == [] and x != 0):
                    next_predictions[data_name] = trainer.histories_buffer[data_name][-1][:x]
                    #print(trainer.histories_buffer[data_name], data_name)

                next_predictions[data_name] += trainer.query_model(data_name, x, y, data_buffers[data_name][x:y+1])
                #next_predictions[data_name] += trainer.query_model(data_name, x, y, serve.parsed_data[data_name][x:y])

                print(len(next_predictions[data_name]))
                assert(len(next_predictions[data_name]) % 15 == 0)

                # print(x, y, time.time()-start)

        return time.time()-start, next_predictions, data_buffers

    def something_else(data_buffers, predictions):
        start = time.time()
        # do something else, must include filling data buffers

        if(trainer.first_call()):
            serve.set_historical_prices()
            trainer.change_historical_data(serve.parsed_data)
            
            for data_name in ['buy_price', 'sell_price', 'demand']:
                previous, most_recent = trainer.get_synthetic_data(data_name)
                trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
                predictions[data_name] = most_recent

        serve.live_data()
        
        print("doing some other stuff")

        for data_name in ['buy_price', 'sell_price', 'demand']:
            data_buffers[data_name].append(serve.parsed_data[data_name])

        return time.time() - start
        
    def main():
        data_buffers = {'buy_price':[], 'sell_price':[], 'demand':[]}
        predictions = {'buy_price':[], 'sell_price':[], 'demand':[]}
        next_predictions = {'buy_price':[], 'sell_price':[], 'demand':[]}

        cycle_count = 0
        
        starting_i = serve.starting_tick()
        i = starting_i

        if(starting_i != 0):
            for k, v in data_buffers.items():
                data_buffers[k] = [0] * starting_i

        print("Started at tick ", starting_i)

        while True:
            if(i == 0):
                cycle_count += 1

                print("Cycle ", cycle_count)
                print()

                time_taken = new_cycle(data_buffers, predictions, next_predictions)

            elif((i % 15) == 0 or (i == 59)):
                time_taken, next_predictions, data_buffers = prepare_next(i, starting_i, data_buffers, next_predictions)

                print("Preparation took ", time_taken)
            
            else:
                # trainer has not been called yet at this point => server didn't start at 0
                # need to set predictions to be entire previous cycle
                time_taken = something_else(data_buffers, predictions)
                print("Something else took ", time_taken)
 
            if(5-time_taken < 0):
                print("Something took too much time ", time_taken)
                sys.exit(1)
            else:
                time.sleep(5-time_taken)
                i = (i + 1) % 60           
            print("Current tick ", i)

    main()



