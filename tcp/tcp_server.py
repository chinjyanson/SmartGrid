import socket
from concurrent.futures import ThreadPoolExecutor
from queue import Queue 
from threading import Thread
import json

class Tcp_server:
    def __init__(self) -> None:
        # using a thread pool to avoid endless thread creation
        self.port = 9998
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', self.port))
        self.picos = {"flywheel": None, "solar":None, "cell":None}

    def handle_client(self, client_socket, queue):
        """Function to handle client connections."""
        while True:
            try: 
                message = client_socket.recv(1024).decode('utf-8')

                print(f"[{str(client_socket.getpeername())}] {message}")
                client_socket.send("Message received".encode('utf-8'))

                if not message:
                    break
                elif (message == "cell" or message == "solar" or message == "flywheel"):
                    self.picos[message] = client_socket
                else:
                    print(f"Message {message} is unknown")
                                 
            except ConnectionResetError:
                break
            
            data = queue.get()
            _data = json.loads(data)

            print(_data)

            try:
                socket = self.picos[_data["type"]]

                if(socket):
                    socket.send(data.encode('utf-8'))
            except KeyError:
                print("Message type in data unknown")

        client_socket.close()

    def start(self, queue : Queue):
        self.server.listen(6)
        print(f"Server started and listening on port {self.port}")
        
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            #pool.submit(self.handle_client, args=(client_socket, queue, ))
            thread = Thread(target=self.handle_client, args=[client_socket, queue])
            thread.start()

if __name__ == "__main__":
    q = Queue()

    tcp_server = Tcp_server()
    tcp_server.start(q)
