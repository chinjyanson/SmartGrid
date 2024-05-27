import numpy as np
import cvxpy as cp
import server_data as data

class SmartGridMPC:
    def __init__(self, storage_capacity=50):
        self.storage_capacity = storage_capacity
        self.storage = 0  # Initial storage level
        self.time_horizon = 60  # 60 time steps (one day)
        self.current_time_step = 0  # Start at the first time step

    def get_solar_energy(self):
        serve = data.server_data()
        # Immediate task data
        serve.live_sunshine()
        area = 10
        sun_energy = serve.parsed_data['sun']
        solar_energy = sun_energy / area
        return solar_energy

    def get_demand(self):
        serve = data.server_data()
        # Immediate task data
        serve.live_demand()
        energy_demand= serve.parsed_data['demand']
        return energy_demand

    def get_prices(self):
        serve = data.server_data()
        serve.live_prices()
        current_buy_price = serve.parsed_data['buy_price']
        current_sell_price = serve.parsed_data['sell_price']
        return current_buy_price, current_sell_price

    def optimize(self, predicted_demand, predicted_buy_price, predicted_sell_price, deferable_demand):
        # Optimization variables
        storage = cp.Variable(self.time_horizon + 1)  # Storage level at each time step
        buy = cp.Variable(self.time_horizon, boolean=True)  # Buy decision (binary) at each time step
        sell = cp.Variable(self.time_horizon, boolean=True)  # Sell decision (binary) at each time step
        use_storage = cp.Variable(self.time_horizon, boolean=True)  # Use stored energy (binary) at each time step
        charge_storage = cp.Variable(self.time_horizon, boolean=True)  # Charge storage (binary) at each time step
        grid = cp.Variable(self.time_horizon)  # Grid energy usage at each time step
        load = cp.Variable(self.time_horizon)  # Load at each time step
        
        # Constraints
        constraints = [
            storage[0] == self.storage,  # Initial storage level
            storage >= 0,  # Storage must be non-negative
            storage <= self.storage_capacity,  # Storage must not exceed capacity
            cp.sum(buy) + cp.sum(sell) <= 1,  # Cannot buy and sell at the same time
            cp.sum(use_storage) + cp.sum(charge_storage) <= 1  # Cannot use and charge storage at the same time
        ]
        
        for t in range(self.time_horizon):
            constraints += [
                load[t] == predicted_demand[t] + deferable_demand[t],  # Load must meet demand
                grid[t] == load[t] - self.get_solar_energy(),  # Balance grid usage
                storage[t + 1] == storage[t] + charge_storage[t] * grid[t] - use_storage[t] * grid[t],  # Update storage level
                buy[t] + sell[t] <= 1,  # Cannot buy and sell at the same time
                use_storage[t] + charge_storage[t] <= 1  # Cannot use and charge storage at the same time
            ]
        
        # Objective function (maximize profit)
        profit = cp.sum(sell * predicted_sell_price - buy * predicted_buy_price)
        
        # Define the optimization problem
        problem = cp.Problem(cp.Maximize(profit), constraints)
        
        # Solve the problem
        problem.solve()
        
        # Extract decisions
        buy_decisions = buy.value
        sell_decisions = sell.value
        use_storage_decisions = use_storage.value
        charge_storage_decisions = charge_storage.value
        storage_levels = storage.value
        return buy_decisions, sell_decisions, use_storage_decisions, charge_storage_decisions, storage_levels

    def run(self):
        while self.current_time_step < self.time_horizon:
            # Get actual current values
            actual_demand = self.get_demand()
            actual_buy_price, actual_sell_price = self.get_prices()
            actual_solar_energy = self.get_solar_energy()
            
            # Update predictions (Placeholder - use actual prediction mechanism)
            predicted_demand = np.array([self.get_demand() for _ in range(self.time_horizon)])
            predicted_buy_price = np.array([self.get_prices()[0] for _ in range(self.time_horizon)])
            predicted_sell_price = np.array([self.get_prices()[1] for _ in range(self.time_horizon)])
            
            # Define deferable demand (Placeholder - use actual deferable demand values)
            deferable_demand = np.zeros(self.time_horizon)
            
            # Optimize
            buy_decisions, sell_decisions, use_storage_decisions, charge_storage_decisions, storage_levels = self.optimize(
                predicted_demand, predicted_buy_price, predicted_sell_price, deferable_demand
            )
            
            # Implement the decision (buy/sell, update storage)
            if buy_decisions[self.current_time_step]:
                self.storage += actual_demand  # Buy energy to meet demand and store the excess
                self.storage = min(self.storage, self.storage_capacity)  # Ensure storage doesn't exceed capacity
            elif sell_decisions[self.current_time_step]:
                self.storage -= actual_demand  # Sell stored energy to meet demand
                self.storage = max(self.storage, 0)  # Ensure storage doesn't go negative

            if use_storage_decisions[self.current_time_step]:
                self.storage -= actual_demand  # Use stored energy to meet demand
                self.storage = max(self.storage, 0)  # Ensure storage doesn't go negative
            elif charge_storage_decisions[self.current_time_step]:
                self.storage += actual_demand  # Charge storage with excess energy
                self.storage = min(self.storage, self.storage_capacity)  # Ensure storage doesn't exceed capacity

            # Print decisions for debugging
            print(f"Time step {self.current_time_step}: Buy - {buy_decisions[self.current_time_step]}, Sell - {sell_decisions[self.current_time_step]}, Use Storage - {use_storage_decisions[self.current_time_step]}, Charge Storage - {charge_storage_decisions[self.current_time_step]}, Storage - {self.storage}")

            # Advance time step
            self.current_time_step += 1

# Example usage
mpc = SmartGridMPC()
mpc.run()
