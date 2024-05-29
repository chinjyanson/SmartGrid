# testing the time it takes to sort and order values pulled from the API

import requests

url = "https://evuc3y0h1g.execute-api.eu-north-1.amazonaws.com/PROD/accessEnergyLog"

response = requests.get(url)
data = response.json()
order_of_days = [entry['dayID'] for entry in data]
print(order_of_days)

num_elements = len(data)

print(f"Number of elements returned: {num_elements}")