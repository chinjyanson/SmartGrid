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

    def get_synthetic_data(self, data_type : str, num_of_available_histories : int) -> tuple[list[list], list]:
        """
            return a tuple of actual data and a set of synthetic data derived from this actual data
        """
        h_data = self.parsed_data[data_type]

        print("Training to synthesize similar data from one previous cycle")

        out = []
        amount = min(self.num_of_histories - num_of_available_histories, 10)

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
                input.append(histories[i][j])   

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
    
    def train_models(self, models : neural_net, histories : list[list[float]], most_recent : list[float]) -> tuple[list[float], list[float]]:
        """
            Train models on a set of histories and return a tuple lists of each model's fitness, and each model's prediction 
        """
        fitnesses = []
        predictions = []

        for model in models:
            # run different copies of the model in parallel on different batches of the histories to make predictions
            # full range is 0->60, make in batches of 15

            batches = batch_up((0, 60), self.data_batch_size)
            prediction = []

            for batch in batches:
                prediction += self.make_prediction(*batch, model, histories)
            
            #prediction = self.train_in_parallel(batches, model, histories)

            fitnesses.append(1 / mse(most_recent, prediction))
            predictions.append(prediction)

        return fitnesses, predictions
    
    def train_on_histories(self, histories, most_recent, pop):
        """
            given a set of histories, and the most recent history, train to predict the cycle of the 
            most recent history
        """
        best_pred = None
        best_fitness = None
        most_recent_pop = None

        for epoch in range(self.epochs):
            print("Epoch: ", epoch+1)

            batches = batch_up((0, pop.size), self.nn_batch_size)
            all_predictions = []

            for x, y in batches:
                fitnesses, predictions = self.train_models(pop.models[x:y], histories, most_recent)
                pop.fitnesses += fitnesses
                all_predictions += predictions

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

        return pop.models[best_model_index], best_fitness, most_recent_pop

    def query_model(self, data : str) -> list[int] | None:
        """
        - this should be called at the beginning of each cycle to predict values for whole cycle
        - it takes some time:
        * the very first time this is called, the histories buffer will be empty, so it has to synthesize it own for prediction training, which is an extra overhead.
        
        Return prediction of next cycle
        """
        print()
        if(data in self.histories_buffer):
            available_histories = self.histories_buffer[data]

            if(len(available_histories) < self.num_of_histories):
                print(f"Not enough histories for {data}, need to synthesize 5 histories for training")
                previous, most_recent = self.get_synthetic_data(data, len(available_histories))
                self.histories_buffer[data] = previous[1:]
                self.histories_buffer[data].append(most_recent)

            else:
                print(f"Have 5 histories for {data}, get most recent data for training")
                previous, most_recent = available_histories, self.parsed_data[data]
                # discard the least recent history, append most recent history, always keep availability of 5
                self.histories_buffer[data] = self.histories_buffer[data][1:]
                self.histories_buffer[data].append(most_recent)  # discard the least recent history, append most recent history, always keep availability of 5
        
            if(self.data_fitnesses[data] != 0): self.fitness_threshold = min(add_noise(self.data_fitnesses[data], 2), 100)

            print("Training on the historical data. Training to predict most recent cycle")
            print("Threshold: ", self.fitness_threshold)

            file_name = os.path.join(self.saved_pop_path, data+".pop")

            old_pop = get_population(file_name)

            if(old_pop):
                pop = Population(old_pop=old_pop)
                print("Loaded previous best population")
            else:
                pop = Population(6, pop_size=50, input_nodes=self.num_of_histories, output_nodes=1, mutation_prob=self.mutation_prob, 
                                elitism=self.elitism, mutation_power=self.mutation_power)
                
                print("Started from random population")

            # train model to predict the most recent cycle given a set of previous cycles
            best_model, best_fitness, best_pop = self.train_on_histories(previous, most_recent, pop)

            # save the best population when this is called. when this function gets called again, it will start from this population of genomes instead of starting randomly
            # save based on a checkpoint, saves every time this function is called by default
            if((Train.call_counter % self.save_checkpoint) == 0):
                save_population(best_pop, file_name)   

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
    trainer = Train(elitism=0.2, mutation_prob=0.08, mutation_power=0.1, max_epochs=65, num_of_histories=5, 
                data_batch_size=15, nn_batch_size=60, parsed_data=serve.parsed_data)
    
    for cycle in range(3):
        print("Cycle ", cycle+1)
        print()
        start = time.time()
        serve.set_historical_prices()
        trainer.change_historical_data(serve.parsed_data)

        buy = trainer.query_model('buy_price')
        sell = trainer.query_model('sell_price')
        demand = trainer.query_model('demand')

        print("Time: ", time.time() - start)
        print()

        plot_datas([buy, serve.parsed_data['buy_price']], "Prediction of current cycle vs prev cycle", "All")
        plot_datas([sell, serve.parsed_data['sell_price']], "Prediction of current cycle vs prev cycle", "All")
        plot_datas([demand, serve.parsed_data['demand']], "Prediction of current cycle vs prev cycle", "All")