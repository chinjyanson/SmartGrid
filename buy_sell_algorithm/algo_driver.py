from queue import Queue 
import time
from predictions.utils import plot_datas, get_sunlight
import sys
from colorama import Fore, Back, Style, init
import optimization as opt
from predictions.train import Train
from data.server_data import server_data
import naive_solution as naive
import json
import test3 as test
from typing import Dict

# Initialize colorama
init(autoreset=True)

#m_Train = module_from_file("Train", "buy_sell_algorithm/predictions/train.py")
#m_data = module_from_file("server_data", "buy_sell_algorithm/data/server_data.py")

class Algorithm:
    def __init__(self) -> None:
        self.serve = server_data()
        self.trainer = Train(elitism=0.2, mutation_prob=0.08, mutation_power=0.1, max_epochs=20, num_of_histories=5, 
                pop_size=60, nn_batch_size=15, parsed_data=self.serve.parsed_data, conc=True)

        self.data_buffers : Dict[str, list[float]] = {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}
        self.old_predictions : Dict[str, list[float]] = {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}
        self.predictions : Dict[str, list[float]] = {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}
        self.next_predictions : Dict[str, list[float]] = {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}
        self.defs = None

        self.cycle_count = 0
        
        self.starting_tick = self.serve.starting_tick(0)

        if(self.serve.error):
            print(Back.CYAN + "Tick value got is incorrect, start again")

        self.window_allowance = 4
        self.tick = self.starting_tick
        self.data_batch_size = 15
        self.buy_to_sell_ratio = 0.5

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
                self.old_predictions[data_name] = most_recent

            self.predictions['sun'] = get_sunlight()
            self.old_predictions['sun'] = get_sunlight()
            
        else:
            print("Current predictions are ready")
            self.old_predictions = self.predictions
            self.old_predictions['sun'] = self.data_buffers['sun']
            self.predictions = self.next_predictions.copy()
            self.predictions['sun'] = self.data_buffers['sun']

        """
        if(self.data_buffers != {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}):
            # previous cycle data buffers are full, we also have what we predicted in self.old_predictions
            for n, p in self.old_predictions.items():
                try:
                    plot_datas([p, self.data_buffers[n]], "Prediction of previous cycle vs Actual data", n)
                except Exception as e:
                    print(f"Exception: {e}")
                    print(len(self.data_buffers[n]), len(p))
        """

        # empty data and next prediction buffers
        for data_name in ['buy_price', 'sell_price', 'demand', 'sun']:
            self.next_predictions[data_name] = []
            self.data_buffers[data_name] = [self.serve.parsed_data[data_name]]

        self.serve.deferables()
        self.defs = self.serve.parsed_data['deferables']


        # self.data_buffers['sun'] = [self.serve.parsed_data['sun']]

        #for n, p in self.predictions.items():
        #    plot_datas([p], "Prediction", n)

        return time.time() - start

    def prepare_next(self):
        """
            - Prepare predictions for the next cycle using the data buffers you have so far
            - Also add value at current tick into data buffer
        """
        start = time.time()
        
        if(not ((self.starting_tick % self.data_batch_size == 0) and self.trainer.first_call())):
            if((0 < self.tick  - self.starting_tick < self.data_batch_size) and self.trainer.first_call()):
                dist = self.tick - self.starting_tick
            else:
                dist = self.data_batch_size

            if(self.tick == 59):
                x, y = 60-dist, 60
            else:
                x, y = self.tick-dist, self.tick

            for data_name in ['sell_price', 'demand']:
                if(self.next_predictions[data_name] == [] and x != 0):
                    self.next_predictions[data_name] = self.trainer.histories_buffer[data_name][-1][:x]
                
                self.next_predictions[data_name] += self.trainer.query_model(data_name, x, y, self.data_buffers[data_name][x:y])

                assert(len(self.next_predictions[data_name]) % self.data_batch_size == 0)

                print(x, y, len(self.next_predictions[data_name]), data_name)

            self.next_predictions['buy_price'] = list(map(lambda x : x*self.buy_to_sell_ratio, self.next_predictions['sell_price']))

        return time.time()-start

    def something_else(self, storage, total_profit):
        start = time.time()
        # do something else, must include filling data buffers

        time_taken = self.add_to_data_buffers()

        print(Fore.MAGENTA + "Adding to data buffers took ", time_taken)

        if(self.trainer.first_call()):
            self.serve.set_historical_prices()
            self.trainer.change_historical_data(self.serve.parsed_data)
            
            for data_name in ['buy_price', 'sell_price', 'demand']:
                previous, most_recent = self.trainer.get_synthetic_data(data_name)
                self.trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
                self.predictions[data_name] = most_recent

            self.serve.deferables()
            self.defs = self.serve.parsed_data['deferables']
        else:
            self.defs = None
        
        # this if else statement changes the prediction horizon when tick > 50 (if horizon = 10)
        profit, storage = test.maximize_profit_mpc(storage, self.data_buffers, self.predictions, self.tick, 60-self.tick, self.defs)

        total_profit += profit

        print(f" ********************************************{total_profit}*******************************************")

        return time.time() - start + time_taken, storage, total_profit
    
    def driver(self, queue : Queue):
        if(self.starting_tick != 0):
            for k, v in self.data_buffers.items():
                if(self.trainer.parsed_data[k] != []):
                    self.data_buffers[k] = self.trainer.parsed_data[k][:self.starting_tick]
                else:
                    self.data_buffers[k] = [0]*self.starting_tick

        print("Started at tick ", self.starting_tick)
        remainder = 0
        storage = 0
        total_profit = 0

        data1 = {"energy":134, "sell":True, "buy":False, "type":"cell"}
        data2 = {"energy":40, "sell":False, "buy":False, "type":"flywheel"}

        while True:
            print(f"Current tick {self.tick}")
            if(self.tick == 0):
                self.cycle_count += 1

                print("Cycle ", self.cycle_count)
                print()
                
                # new cycle should always come before something_else such that data buffers get emptied
                time_taken = self.new_cycle()
                tt, storage, total_profit = self.something_else(storage, total_profit)
                time_taken += tt
                remainder = 5-time_taken 
                print(Fore.MAGENTA + f"Setting up new cycle took {time_taken}s", (Fore.GREEN if remainder > 1.5 else Fore.LIGHTRED_EX) + f"Window [{remainder}s]")

            elif((self.tick % self.data_batch_size) == 0 or (self.tick == 59)):
                time_taken, storage, total_profit = self.something_else(storage, total_profit)
                time_taken += self.prepare_next()
                remainder = 5-time_taken
                print(Fore.YELLOW + f"Preparation and decision took {time_taken}s", (Fore.GREEN if remainder > 1.5 else Fore.LIGHTRED_EX) + f"Window [{remainder}s]")
            
            else:
                time_taken, storage, total_profit = self.something_else(storage, total_profit)
                remainder = 5-time_taken
                print(Fore.BLUE + f"Something else and adding to data buffers took {time_taken}s", (Fore.GREEN if remainder > 1.5 else Fore.LIGHTRED_EX) + f"Window [{remainder}s]")

            if(remainder < -self.window_allowance):
                print(Fore.RED + "Something took too much time ", time_taken)
                print(Fore.RED + "Final tick was ", self.tick)
                sys.exit(1)
            else:
                old_tick = self.tick
                self.tick = self.serve.starting_tick(self.tick)

                if(self.tick == old_tick):
                    print(Back.GREEN + "Got an error when getting live tick, tick is changed after sleep")
                    if(remainder - self.serve.live_timeout > -self.window_allowance):
                        time.sleep(remainder - self.serve.live_timeout)
                        self.tick = (self.tick + 1) % 60 
                    else:
                        print(Fore.RED + "Something took too much time ", time_taken + self.serve.live_timeout)
                        sys.exit(1)

                diff = old_tick - self.tick
                
                if(not(diff == -1 or diff == 59 or diff == self.tick)):
                    print(Back.LIGHTYELLOW_EX + f"Tick mismatch old: {old_tick}, new: {self.tick}")
                    self.tick = old_tick

            queue.put(json.dumps(data1))
            queue.put(json.dumps(data2))

if __name__ == "__main__":
    q = Queue()

    algo = Algorithm()
    algo.driver(q)
