from predictions.utils import module_from_file
from threading import Thread
import asyncio
from algo_driver import Algorithm

m_tcp = module_from_file("Tcp_server", "tcp/tcp_server.py")

def entrypoint(method, *params):
    asyncio.run(method(*params))

def main():
    algo = Algorithm()
    tcp_server = m_tcp.Tcp_server()

    algo_thread = Thread(target=algo.driver)
    tcp_thread = Thread(target=tcp_server.start)

    algo_thread.start()
    tcp_thread.start()

    algo_thread.join()
    tcp_thread.join()

main()
