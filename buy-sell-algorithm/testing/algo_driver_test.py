from train_test import Train
from server_data_test import server_data
import asyncio
import time
from helper_test import plot_datas, batch_up
import sys
from colorama import Fore, Back, Style, init
import MPC_solution_test as opt
import naive_solution_test as naive

# Initialize colorama
init(autoreset=True)

class Algorithm:
    def __init__(self) -> None:
        self.serve = server_data()
        self.trainer = Train(elitism=0.2, mutation_prob=0.08, mutation_power=0.1, max_epochs=20, num_of_histories=5, 
                data_batch_size=15, nn_batch_size=60, parsed_data=self.serve.parsed_data)
        self.event_loop = asyncio.get_event_loop()

        self.data_buffers = {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}
        self.predictions = {'buy_price':[], 'sell_price':[], 'demand':[]}
        self.next_predictions = {'buy_price':[], 'sell_price':[], 'demand':[]}

        self.cycle_count = 0
        
        self.starting_tick = self.serve.starting_tick()
        self.tick = self.starting_tick

    def add_to_data_buffers(self):
        start = time.time()
        self.serve.live_data()
        for data_name, data in self.data_buffers.items():
            data.append(self.serve.parsed_data[data_name])

        return time.time() - start

    def new_cycle(self):
        """
            - Set prediction of current cycle to be the most recent history if this is first call to trainer at tick 0
            - If this is not first call to trainer at tick 0, then next predictions should become current predictions
            - Empty data and next predictions buffers, add current values into data buffers to begin with
        """
        start = time.time()

        # at start of new cycle, prepare predictions for current cycle, and set correct historical data
        self.serve.set_historical_prices()
        self.trainer.change_historical_data(self.serve.parsed_data)

        if(self.trainer.first_call()):
            print("First call, assume predictions for all data is most recent cycle")
            
            for data_name, _ in self.trainer.histories_buffer.items():
                previous, most_recent = self.trainer.get_synthetic_data(data_name)
                self.trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
                self.predictions[data_name] = most_recent
            
        else:
            print("Current predictions are ready")
            if any([len(n) == 0 for n in self.next_predictions.values()]):
                self.predictions = self.trainer.histories_buffer
            else:
                self.predictions = self.next_predictions.copy()

        # empty data and next prediction buffers and add the current live values
        self.serve.live_data()
        
        for data_name in ['buy_price', 'sell_price', 'demand']:
            self.next_predictions[data_name] = []
            self.data_buffers[data_name] = []
            self.data_buffers[data_name].append(self.serve.parsed_data[data_name])

        self.data_buffers['sun'] = []
        self.data_buffers['sun'].append(self.serve.parsed_data['sun'])

        # for n, p in self.predictions.items():
        #     plot_datas([p], "Prediction", n)

        return time.time() - start

    def prepare_next(self):
        """
            - Prepare predictions for the next cycle using the data buffers you have so far
            - Also add value at current tick into data buffer
        """
        start = time.time()
        # prepare next predictions for next batch each time we are at tick 15, 30, 45, 60
        
        if(not ((self.starting_tick % 15 == 0) and self.trainer.first_call())):
            if((0 < self.tick  - self.starting_tick < 15) and self.trainer.first_call()):
                dist = self.tick - self.starting_tick
            else:
                dist = 15

            if(self.tick == 59):
                x, y = 60-dist, 60
            else:
                x, y = self.tick-dist, self.tick


            for data_name in ['buy_price', 'sell_price', 'demand']:

                if(self.next_predictions[data_name] == [] and x != 0):
                    self.next_predictions[data_name] = self.trainer.histories_buffer[data_name][-1][:x]
                
                self.next_predictions[data_name] += self.trainer.query_model(data_name, x, y, self.data_buffers[data_name][x:y])

                assert(len(self.next_predictions[data_name]) % 15 == 0)

                print(x, y, len(self.next_predictions[data_name]))

        return time.time()-start

    def something_else(self, storage, naive_storage):
        start = time.time()
        # do something else, must include filling data buffers

        time_taken = self.add_to_data_buffers()

        if(self.trainer.first_call()):
            self.serve.set_historical_prices()
            self.trainer.change_historical_data(self.serve.parsed_data)
            
            for data_name in ['buy_price', 'sell_price', 'demand']:
                previous, most_recent = self.trainer.get_synthetic_data(data_name)
                self.trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
                self.predictions[data_name] = most_recent
        
        print("Running Ansons Code")
        # this if else statement changes the prediction horizon when tick > 50 (if horizon = 10)
        if self.tick >= 50:
            profit, storage = opt.maximize_profit_mpc(storage, self.data_buffers, self.predictions, self.tick, 60-self.tick)
        else:
            profit, storage = opt.maximize_profit_mpc(storage, self.data_buffers, self.predictions, self.tick, 10)

        naive_profit, naive_storage = naive.naive_smart_grid_optimizer(self.data_buffers, self.tick, naive_storage)

        profit_difference_tick = profit-naive_profit

        print(f"DIFFERENCE IN PROFIT: {profit_difference_tick}")

        return time.time() - start + time_taken, storage, naive_storage, profit_difference_tick
    
    def driver(self):
        if(self.starting_tick != 0):
            for k, v in self.data_buffers.items():
                self.data_buffers[k] = [0] * self.starting_tick

        print("Started at tick ", self.starting_tick)
        remainder = 0
        storage = 0
        naive_storage = 0
        total_profit_difference = 0

        while True:
            print(f"Current tick {self.tick}")
            if(self.tick == 0):
                self.cycle_count += 1

                print("Cycle ", self.cycle_count)
                print()

                time_taken = self.new_cycle()
                remainder = 5-time_taken
                print(Fore.MAGENTA + f"Setting up new cycle took {time_taken}s", (Fore.GREEN if remainder > 1.5 else Fore.LIGHTRED_EX) + f"Window [{remainder}s]")

            elif((self.tick % 15) == 0 or (self.tick == 59)):
                time_taken1, storage, naive_storage, profit_difference_tick = self.something_else(storage, naive_storage)
                time_taken2 = self.prepare_next()
                time_taken = time_taken1 + time_taken2
                remainder = 5-time_taken
                print(Fore.YELLOW + f"Preparation and decision took {time_taken}s", (Fore.GREEN if remainder > 1.5 else Fore.LIGHTRED_EX) + f"Window [{remainder}s]")
            
            else:
                time_taken, storage, naive_storage, profit_difference_tick = self.something_else(storage, naive_storage)
                remainder = 5-time_taken
                print(Fore.BLUE + f"Something else and adding to data buffers took {time_taken}s", (Fore.GREEN if remainder > 1.5 else Fore.LIGHTRED_EX) + f"Window [{remainder}s]")

            if(remainder < 0):
                print(Fore.RED + "Something took too much time ", time_taken)
                print(Fore.RED + "Final tick was ", self.tick)
                sys.exit(1)
            else:
                time.sleep(remainder)
                self.tick = (self.tick + 1) % 60   

            total_profit_difference += profit_difference_tick
            print(f"**********************************{total_profit_difference}**********************************")

if __name__ == "__main__":
    while True:
        algo = Algorithm()
        algo.driver()

