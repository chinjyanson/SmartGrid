import sys, os

train_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))

if train_root not in sys.path:
    sys.path.insert(0, train_root)

from neural_net import Population, neural_net
import numpy as np
from utils.helper import module_from_file, mse, plot_datas, save_population, get_population, add_noise, batch_up
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import time

m_server = module_from_file("server_data", "buy-sell-algorithm/data/server_data.py")
m_made = module_from_file("Data", "buy-sell-algorithm/data/datavis.py")

serve = m_server.server_data()

class Train:
    """
        Train models using a genetic algorithm to synthesize data if needed, and predict data in a cycle
    """
    call_counter = 0

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

        pop = Population(4, 4, pop_size=10, input_nodes=2, output_nodes=1, mutation_prob=self.mutation_prob, mutation_power=self.mutation_power, elitism=self.elitism)
        best_model = None
        data_points = 60

        # training
        for epoch in range(50):
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
            
            if(not(epoch % 10) and len(out) < amount):
                out.append(synthetics[best_model])

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
                    print(e, ", index: ", j) 
                    sys.exit(1)  

            prediction.append(model.query(input)[0][0])

        return prediction
    
    def train_in_parallel(self, batches, model, histories):
        tasks = []

        for batch in batches:
            tasks.append((*batch, model, histories))

        prediction = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_prediction = [executor.submit(self.make_prediction, *task) for task in tasks]

            for future in as_completed(future_to_prediction):
                prediction += future.result()

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
            
            # prediction = self.train_in_parallel(batches, model, histories)

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
        
        #plot_datas([best_pred, most_recent], "Best prediction of most recent cycle", "Data")

        # save the best population when this is called. when this function gets called again, it will start from this population of genomes instead of starting randomly
        # save based on a checkpoint, saves every time this function is called by default
        if((Train.call_counter % self.save_checkpoint) == 0):
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

            if(start_index == 0):
                self.histories_buffer[data_name] = previous[1:] + [most_recent]
            else:
                self.histories_buffer[data_name][-1] += most_recent
            
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

    trainer = Train(elitism=0.2, mutation_prob=0.08, mutation_power=0.1, max_epochs=65, num_of_histories=5, 
                data_batch_size=15, nn_batch_size=60, parsed_data=serve.parsed_data)
    
    cycles = sum([[i for i in range(60)] for _ in range(3)], [])

    data_buffers = {'buy_price':[], 'sell_price':[], 'demand':[]}
    predictions = {'buy_price':[], 'sell_price':[], 'demand':[]}
    next_predictions = {'buy_price':[], 'sell_price':[], 'demand':[]}

    cycle_count = 0
    
    for i in cycles:

        if(i == 0):
            # at start of new cycle, prepare predictions for current cycle, and set correct historical data
            cycle_count += 1

            print("Cycle ", cycle_count)
            print()

            serve.set_historical_prices()
            trainer.change_historical_data(serve.parsed_data)

            if(trainer.first_call()):
                print("First call, assume predictions for all data is most recent cycle")
                
                for data_name in ['buy_price', 'sell_price', 'demand']:
                    previous, most_recent = trainer.get_synthetic_data(data_name)
                    trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
                    predictions[data_name] = most_recent
                
            else:
                print("Current predictions are ready")
                predictions = next_predictions.copy()

            # empty data and next prediction buffers and add the current live values
            """
            serve.live_prices()
            serve.live_demand()
            """
            for data_name in ['buy_price', 'sell_price', 'demand']:
                data_buffers[data_name] = []
                next_predictions[data_name] = []
                data_buffers[data_name].append(serve.parsed_data[data_name])
            
            for d, pred in predictions.items():
                plot_datas([pred, serve.parsed_data[d]], "Prediction of current cycle vs prev cycle", "All")

        elif((i % 15) == 0 or (i == 59)):
            # prepare next predictions for next batch each time we are at tick 15, 30, 45, 60
            # start a new thread that does this batch while another thread continues on with the for loop
            if(i == 59):
                x, y = 45, 60
            else:
                x, y = batch_up((i-15, i), 15)[0]

            """ 
            serve.live_prices()
            serve.live_demand()
            """
            for data_name in ['buy_price', 'sell_price', 'demand']:
                data_buffers[data_name].append(serve.parsed_data[data_name])
        
            for data_name in ['buy_price', 'sell_price', 'demand']:
                print(x, y)
                #next_predictions[data_name] += trainer.query_model(data_name, x, y, data_buffers[data_name][x:y])
                next_predictions[data_name] += trainer.query_model(data_name, x, y, serve.parsed_data[data_name][x:y])

        else:
            # do something else, must include filling data buffers
            """
            serve.live_prices()
            serve.live_demand()
            """
            for data_name in ['buy_price', 'sell_price', 'demand']:
                data_buffers[data_name].append(serve.parsed_data[data_name])

