from predictions.utils import module_from_file
from multiprocessing import Process, Queue
from algo_driver import Algorithm
#from queue import Queue 

m_tcp = module_from_file("run_server", "tcp/tcp_server.py")
m_driver = module_from_file("driver", "tcp/fake_algo.py")
q = Queue()

def main():
    #init_frontend_file()
    # algorithm runs in main process
    algo = Algorithm()
    server_host = '0.0.0.0'
    server_port = 5559 

    # tcp server runs in seperate process
    tcp_process = Process(target=m_tcp.start_server, args=(server_host, server_port, q, ))
    tcp_process.start()
    algo.driver(q)
     
    tcp_process.join()

if __name__ == "__main__":
    main() 