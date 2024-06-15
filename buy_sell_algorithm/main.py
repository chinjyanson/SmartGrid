from predictions.utils import module_from_file
from threading import Thread
from algo_driver import Algorithm
from queue import Queue 

m_tcp = module_from_file("start_server", "tcp/anson_ver/tcp_server.py")

q = Queue()
server_host = '0.0.0.0'
server_port = 5555

def main():
    algo = Algorithm()

    algo_thread = Thread(target=algo.driver, args=(q, ))
    tcp_thread = Thread(target=m_tcp.start_server, args=(server_host, server_port, q, ))

    algo_thread.start()
    tcp_thread.start()

    algo_thread.join()
    tcp_thread.join()


if __name__ == "__main__":
    main()