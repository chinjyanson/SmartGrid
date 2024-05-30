import requests
from tabulate import tabulate

# I want to tabulate the data and display it as well as plot a graph of the json data given
import matplotlib.pyplot as plt

# Make the API call
response = requests.get('https://evuc3y0h1g.execute-api.eu-north-1.amazonaws.com/PROD/accessEnergyLog')
if response.status_code != 200:
    print('Error:', response.status_code)
    exit()

# Extract the values from the API response
data = response.json()
data.sort(key=lambda item: item['dayID'])
x_values = [item['dayID'] for item in data]
y_values = [item['energyProduced'] for item in data]
avg_sun_irradiance = [item['avgSunIrradiance'] for item in data]

# Plot the graph
plt.plot(x_values, avg_sun_irradiance, label='Average Sun Irradiance')
plt.xlabel('Day')
plt.ylabel('Sun Irradiance')
plt.title('Day VS Average Sun Irradiance')
plt.legend()
plt.show()

# Create a list of rows for the table
table_data = []
for item in data:
    table_data.append([item['dayID'], item['energyProduced'], item['avgSunIrradiance']])

# Display the table in the terminal
print(tabulate(table_data, headers=['Day', 'Energy Produced', 'Average Sun Irradiance']))

# Plot the graph
plt.plot(x_values, y_values, label='Energy Produced')
plt.xlabel('Day')
plt.ylabel('Energy Produced')
plt.title('Day VS Energy Produced')
plt.legend()
plt.show()

# Create a list of rows for the table
table_data = []
for item in data:
    table_data.append([item['dayID'], item['energyProduced']])

# Display the table in the terminal
print(tabulate(table_data, headers=['Day', 'Energy Produced']))