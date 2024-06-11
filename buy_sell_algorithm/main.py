from predictions.utils import module_from_file
from threading import Thread
import asyncio
from algo_driver import Algorithm
from queue import Queue 
import os 
from pathlib import Path
import json

m_tcp = module_from_file("Tcp_server", "tcp/tcp_server.py")
project_dir = os.getcwd()

q = Queue()

def main():
    algo = Algorithm()
    tcp_server = m_tcp.Tcp_server()

    algo_thread = Thread(target=algo.driver, args=(q, ))
    tcp_thread = Thread(target=tcp_server.start, args=(q, ))

    algo_thread.start()
    tcp_thread.start()

    algo_thread.join()
    tcp_thread.join()

def generate_json():
    json_path = os.path.join(project_dir, "react-front-end", "data.json")

    # Data to be written to the JSON file
    new_data = {"message": "Hello World!"}

    # If the JSON file already exists, read the existing data
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # If file is empty or not valid JSON, start with an empty list
    else:
        data = []  # Start with an empty list if file doesn't exist

    # Append new data
    data.append(new_data)

    # Write the updated data back to the JSON file
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

generate_json()