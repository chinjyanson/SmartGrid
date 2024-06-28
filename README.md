# Smart Grid

## About
In the evolving landscape of energy management, the integration of renewable energy sources with advanced grid systems presents a significant opportunity to enhance efficiency and sustainability. Our project aims to develop a cutting-edge smart grid system that leverages machine learning and optimization algorithms to predict and manage energy trading with an external grid. This system will incorporate an internal solar array to harness renewable energy and make real-time decisions on energy storage, usage, selling, and buying.

The smart grid model will simulate a single day with each minute represented by a 5-minute interval, allowing for detailed analysis and optimization of energy flows. The system will be equipped with six microcontrollers: three dedicated to managing load usage and three connected to a Switched-Mode Power Supply (SMPS) module that governs the energy flow decisions. By utilizing predictive analytics and an optimization framework, our smart grid will aim to maximize economic and energy efficiency while minimizing reliance on external energy sources.

Key components of the project include:

- **Internal Solar Array:** A renewable energy source that will provide power for the grid.
- **Machine Learning Predictive Models:** To forecast energy production and consumption patterns.
- **Optimization Algorithms:** To make informed decisions on whether to store energy, use it, sell it back to the grid, or purchase additional energy.
- **Microcontroller Management:** Six microcontrollers with distinct roles—three for load management and three for energy flow control via the SMPS module.

This project not only addresses the current challenges of energy management but also sets the stage for future advancements in smart grid technologies. By implementing this model, we aim to demonstrate the potential for intelligent, data-driven energy systems to revolutionize how energy is produced, distributed, and consumed.


## Members

| Name                 | Course | CID      | Main Tasks Assigned                     |
| -------------------- | ------ | -------- | --------------------------------------- |
| Anson Chin Jun Yen   | EIE    | 02194736 | Buy-Sell Algo                           |
| Samuel Khoo Ing Shin | EIE    | 02264291 | API Development and Web Application     |
| Ilan Iwumbwe         | EIE    | 02211662 | Buy Sell Algo and Microcontroller       |
| Eddie Moualek        | EEE    | 02029589 | Hardware                                |
| Justin Lam           | EEE    | 02210573 | Hardware                                |
| Lucas Lasanta        | EEE    | 02236286 | Hardware                                |

## Running the code

Install all required dependencies using `pip install -r requirements.txt`

## Top Level Design

![alt text](https://github.com/chinjyanson/SmartGrid/blob/main/images/TopLevel.drawio.png)


## Buy Sell Algorithm
### Machine Learning Predictions
Genetic algorithm was made from scratch, which trains a population of neural networks to predict buy
price, sell price and demand. A genetic algorithm is inspired heavily by evolutionary principles. It tries
to find a good local minima of loss on a problem by hand picking neural networks with good weights in a
tournament pool. Start with a set of n neural nets, each with randomized weights. Run each neural net on
the prediction problem, and by comparing its prediction with the actual values, work out the fitness of the
neural network. The reciprocal of mean squared error was used as our fitness score. Create a new population
of neural networks using this fitness information. The top k% (elitism) of neural nets are passed directly to
the new population. The rest is filled by doing a crossover and mutation step. Crossover refers to picking
weights from 2 parent neural nets to form a child neural net. Mutation refers to adding random noise to
the weights. This process is repeated over multiple epochs. All parameters are easily tunable via a top-level
interface.

### Optimization 
Primarily made possible by a Coin and Branch or Cut Solver, which is a Mixed Integer Linear Programming library that works based on this flowchart below:
![alt text](https://github.com/chinjyanson/SmartGrid/blob/main/images/CBC.png)
We make the prediction window `60-ticks` since the new predictions only come in every 60 ticks. That means that the outputs for our cp variables will be an array of length `60-ticks` and the CBC solver accounts for the best set of values of all variables to create the maximum profit. Obviously the predicted values does not always equate to the actual value, hence we always re-run the CBC solver at each tick (almost like recalibrating)

## Webserver 
### Dashboard
Primarily shows the tick by tick comparisons and decisions. It shows in particular the:
- Whether we are buying or selling in the tick
- Historical data on storage
- MILP Algorithm vs Naive Solution
### Consumption Page 
![alt text](https://github.com/chinjyanson/SmartGrid/blob/main/images/consumptions.png)
### Finance Page
![alt text](https://github.com/chinjyanson/SmartGrid/blob/main/images/finances.png)

## Making the APIs


## Testing


## TCP Connections 





