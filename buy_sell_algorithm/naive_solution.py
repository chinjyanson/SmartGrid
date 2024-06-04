import data.server_data as data
from predictions.train import Train
import time

'''
most naive solution to the problem
'''

#Logic: 
#

def get_current_energy_in():
    serve = data.server_data()
    serve.live_sunshine()
    area = 10
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area
    return solar_energy

def get_deferred_energy():
    serve = data.server_data()
    serve.deferables()
    deferred_start = serve.parsed_data['start']
    deferred_end = serve.parsed_data['end']
    deferred_energy = serve.parsed_data['energy']
    return deferred_start, deferred_end, deferred_energy

def get_current_energy_used():
    serve = data.server_data()
    serve.live_demand()
    energy_demand= serve.parsed_data['demand']
    return energy_demand

def get_current_buy_sell_prices():
    serve = data.server_data()
    serve.live_prices()
    current_buy_price = serve.parsed_data['buy_price']
    current_sell_price = serve.parsed_data['sell_price']
    return current_buy_price, current_sell_price

predicted_buy_prices = [0.97884838, 0.89573551, 0.75651526, 0.36626735, 0.09419675, 0.54257027, 
 0.68039317, 0.87333353, 0.19739547, 0.72302134, 0.67173916, 0.48412507, 
 0.64624241, 0.71897936, 0.98373854, 0.06747502, 0.31398806, 0.41772002, 
 0.75193036, 0.19930055, 0.160341  , 0.36658717, 0.09247076, 0.36090448, 
 0.62623211, 0.18597056, 0.04352059, 0.98483265, 0.27374228, 0.16594721, 
 0.07075692, 0.9261148 , 0.38126222, 0.61062392, 0.28653422, 0.705676  , 
 0.98333091, 0.35057567, 0.59573134, 0.40687669, 0.01086977, 0.11556685, 
 0.56960304, 0.91324145, 0.37973758, 0.99515715, 0.49952499, 0.4567768 , 
 0.06356873, 0.14114093, 0.25821279, 0.86992217, 0.31056673, 0.35155208, 
 0.67007042, 0.78291179, 0.84905628, 0.77026262, 0.01048405, 0.86917204]

predicted_sell_prices = [0.03194762, 0.45930612, 0.01051858, 0.69079694, 0.51206006,
 0.77535087, 0.10057117, 0.49460835, 0.91203877, 0.08952572,
 0.19057528, 0.01690927, 0.95617028, 0.30402571, 0.45785883,
 0.47598909, 0.84453514, 0.68161295, 0.14620774, 0.42293036,
 0.04753764, 0.63428545, 0.73821707, 0.28639252, 0.20461561,
 0.09949421, 0.01097188, 0.04416948, 0.96547974, 0.66680281,
 0.10233287, 0.27461902, 0.20731588, 0.49069655, 0.98324785,
 0.95886353, 0.02241813, 0.06577477, 0.27708673, 0.6320764 ,
 0.69405073, 0.77769733, 0.54160703, 0.32145207, 0.72802205,
 0.31492333, 0.20378386, 0.16166824, 0.67808081, 0.44890131,
 0.25668703, 0.43767515, 0.15153876, 0.62236015, 0.60261888,
 0.48828462, 0.96621227, 0.06060192, 0.44209771, 0.62306391]

predicted_demand = [0.68930846, 0.7082086 , 0.63636331, 0.5988409 , 0.30544195, 0.56052397, 
 0.68879429, 0.10792174, 0.17517828, 0.74036328, 0.15188816, 0.37261624, 
 0.87794606, 0.01026152, 0.76184164, 0.35642952, 0.70981649, 0.71206344, 
 0.15269325, 0.65844334, 0.9797104 , 0.63554534, 0.86394503, 0.17172609, 
 0.24588671, 0.83785965, 0.60799301, 0.1629502 , 0.0107552 , 0.89666861, 
 0.18507491, 0.60574117, 0.08043728, 0.23206797, 0.10741447, 0.9662969 , 
 0.31287944, 0.97211659, 0.62436168, 0.835991  , 0.85975781, 0.25064835, 
 0.98911537, 0.68811079, 0.68311063, 0.29208098, 0.40444325, 0.71085552, 
 0.40141714, 0.74311895, 0.07343258, 0.62053059, 0.10417085, 0.90518443, 
 0.18302153, 0.70323316, 0.33956219, 0.20709873, 0.08862838, 0.14611133]


initial_buffer_level = 0
max_buffer_capacity = 50


# Constants
STORAGE_CAPACITY = 50  # Maximum storage capacity in Joules

# Variables
current_storage = 0  # Initialize the storage to 0
total_profit = 0 

# Placeholder for deferable demand properties (start, end, energy required)
deferable_demand = [(10, 20, 30), (30, 50, 20)]  # Example deferable demands

def naive_smart_grid_optimizer():
    global current_storage, total_profit

    for t in range(60):
        # Get actual values
        solar_energy = get_current_energy_in()
        actual_demand = get_current_energy_used()
        buy_price, sell_price = get_current_buy_sell_prices()

        # Total energy needed
        total_demand = actual_demand
        
        # Schedule deferable demand within its window
        for start, end, energy in deferable_demand:
            if start <= t < end:
                total_demand += energy / (end - start)  # Spread energy requirement over time window

        # Use solar energy first to meet demand
        if solar_energy >= total_demand:
            solar_energy -= total_demand
            total_demand = 0
        else:
            total_demand -= solar_energy
            solar_energy = 0

        # Use stored energy if solar is insufficient
        if total_demand > 0:
            if current_storage >= total_demand:
                current_storage -= total_demand
                total_demand = 0
            else:
                total_demand -= current_storage
                current_storage = 0

        # Buy energy from the grid if necessary
        if total_demand > 0:
            # Buy enough energy to meet the remaining demand
            energy_bought = total_demand
            total_profit -= energy_bought * buy_price  # Subtract the cost of buying energy
            current_storage += energy_bought
            current_storage = min(current_storage, STORAGE_CAPACITY)  # Ensure storage does not exceed capacity

        # Handle excess solar energy
        if solar_energy > 0:
            # First try to store the excess energy
            if current_storage + solar_energy <= STORAGE_CAPACITY:
                current_storage += solar_energy
            else:
                # If storage is full, sell the excess energy
                excess_energy = current_storage + solar_energy - STORAGE_CAPACITY
                total_profit += excess_energy * sell_price  # Add the revenue from selling energy
                current_storage = STORAGE_CAPACITY

        # Print current state for debugging
        print("for cycle: " + str(t))
        print(f"Time {t}: Demand={actual_demand}, Solar={solar_energy}, Storage={current_storage}, Buy Price={buy_price}, Sell Price={sell_price}")
        print(f"Total Profit={total_profit}")

    return total_profit


def get_total_profit():
    return total_profit

# Run the optimizer
print(naive_smart_grid_optimizer())

# Get the total profit
print("Total Profit: ", get_total_profit())