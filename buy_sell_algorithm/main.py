from predictions.utils import module_from_file, init_frontend_file
from threading import Thread
#from algo_driver import Algorithm
from queue import Queue 

m_tcp = module_from_file("run_server", "tcp/tcp_server.py")
a_tcp = module_from_file("driver", "tcp/fake_algo.py")
q = Queue()

host = '0.0.0.0'
port = 5552

def main():
    #init_frontend_file()

    #algo = Algorithm()
    server_host = '0.0.0.0'
    server_port = 5555  


    algo_thread = Thread(target=a_tcp.driver, args=(q, ))
    tcp_thread = Thread(target=m_tcp.start_server, args=(server_host, server_port, q, ))

    algo_thread.start()
    tcp_thread.start()

    algo_thread.join()
    tcp_thread.join()

if __name__ == "__main__":
    main()