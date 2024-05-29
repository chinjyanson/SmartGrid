import requests
import json
import time

def call_api(day):
    # Making the HTTP request to the web link
    response = requests.get("https://icelec50015.azurewebsites.net/yesterday")

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        # Calculate the sum of all the demand values
        total_demand = sum(entry['demand'] for entry in data)
        print("Total demand:", total_demand)

        # Performing the API post with the extracted information
        post_data = {"dayID": day, "energyUsed": total_demand}
        response = requests.post("https://evuc3y0h1g.execute-api.eu-north-1.amazonaws.com/PROD/accessUsageLog", json=post_data)
        print("successful post") if response.status_code == 200 else print("failed post")
    else:
        print("Failed to retrieve data from the web link.")

def run_api_calls():
    day = 1
    while True:
        call_api(day)
        day += 1
        time.sleep(300)  # Sleep for 5 minutes (300 seconds)

run_api_calls()
# call_api()