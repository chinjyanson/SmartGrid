from predictions.train import Train
from data.server_data import server_data
import asyncio
import time
from predictions.utils.helper import plot_datas, batch_up
import sys

serve = server_data()

trainer = Train(elitism=0.2, mutation_prob=0.08, mutation_power=0.1, max_epochs=20, num_of_histories=5, 
            data_batch_size=15, nn_batch_size=60, parsed_data=serve.parsed_data)
loop = asyncio.get_event_loop()

def add_to_data_buffers(data_buffers):
    start = time.time()
    serve.live_data()
    for data_name in ['buy_price', 'sell_price', 'demand', 'sun']:
        data_buffers[data_name].append(serve.parsed_data[data_name])

    return time.time() - start

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
        next_predictions[data_name] = []
        data_buffers[data_name] = []
        data_buffers[data_name].append(serve.parsed_data[data_name])

    data_buffers['sun'] = []
    data_buffers['sun'].append(serve.parsed_data['sun'])

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
   
    time_taken1 = add_to_data_buffers(data_buffers)
    
    if(not ((starting_i % 15 == 0) and (trainer.first_call())) or (starting_i < 30)):
        if(0 < i  - starting_i < 15):
            dist = i - starting_i
        else:
            dist = 15

        if(i == 59):
            x, y = 60-dist, 60
        else:
            x, y = batch_up((i-dist, i), dist)[0]


        for data_name in ['buy_price', 'sell_price', 'demand']:

            if(next_predictions[data_name] == [] and x != 0):
                next_predictions[data_name] = trainer.histories_buffer[data_name][-1][:x]
            
            next_predictions[data_name] += trainer.query_model(data_name, x, y, data_buffers[data_name][x:y+1])
          
            print(len(next_predictions[data_name]))
            assert(len(next_predictions[data_name]) % 15 == 0)

    return time.time()-start + time_taken1, next_predictions, data_buffers

def something_else(predictions):
    start = time.time()
    # do something else, must include filling data buffers

    if(trainer.first_call()):
        serve.set_historical_prices()
        trainer.change_historical_data(serve.parsed_data)
        
        for data_name in ['buy_price', 'sell_price', 'demand']:
            previous, most_recent = trainer.get_synthetic_data(data_name)
            trainer.histories_buffer[data_name] = previous[1:] + [most_recent]
            predictions[data_name] = most_recent
    
    print("doing some other stuff")

    # decision from Anson's algorithm   

    return time.time() - start
    
def main():
    data_buffers = {'buy_price':[], 'sell_price':[], 'demand':[], 'sun':[]}
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
            time_taken1 = something_else(predictions)
            time_taken2, next_predictions, data_buffers = prepare_next(i, starting_i, data_buffers, next_predictions)
            time_taken = time_taken1 + time_taken2
            print("Preparation and decision took ", time_taken)
        
        else:
            time_taken1 = add_to_data_buffers(data_buffers)
            time_taken2 = something_else(predictions)
            time_taken = time_taken1 + time_taken2
            print("Something else and adding to data buffers took ", time_taken)

        if(5-time_taken < 0):
            print("Something took too much time ", time_taken)
            sys.exit(1)
        else:
            time.sleep(5-time_taken)
            i = (i + 1) % 60           
        print("Current tick ", i)

if __name__ == "__main__":
    main()

