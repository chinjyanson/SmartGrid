from predictions.utils import module_from_file, add_data_to_frontend_file, init_frontend_file
from threading import Thread, Lock
from algo_driver import Algorithm
from queue import Queue 
import os 
from typing import Dict

import json

m_tcp = module_from_file("Tcp_server", "tcp/tcp_server.py")

q = Queue()


def main():
    init_frontend_file()

    algo = Algorithm()
    tcp_server = m_tcp.Tcp_server()

    algo_thread = Thread(target=algo.driver, args=(q, ))
    tcp_thread = Thread(target=tcp_server.start, args=(q, ))

    algo_thread.start()
    tcp_thread.start()

    algo_thread.join()
    tcp_thread.join()

main()