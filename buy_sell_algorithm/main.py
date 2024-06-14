from predictions.utils import module_from_file, init_frontend_file
from threading import Thread
from algo_driver import Algorithm
from queue import Queue 

m_tcp = module_from_file("run_server", "tcp/tcp_server_II.py")
q = Queue()


def main():
    init_frontend_file()

    algo = Algorithm()

    algo_thread = Thread(target=algo.driver, args=(q, ))
    tcp_thread = Thread(target=m_tcp.run_server, args=(q, ))

    algo_thread.start()
    tcp_thread.start()

    algo_thread.join()
    tcp_thread.join()

if __name__ == "__main__":
    main()