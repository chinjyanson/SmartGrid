import socket
from concurrent.futures import ThreadPoolExecutor
from queue import Queue 

class Tcp_server:
    def __init__(self) -> None:
        # using a thread pool to avoid endless thread creation
        self.pool = ThreadPoolExecutor(max_workers=6)
        self.port = 9999
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', self.port))
        self.picos = {"flywheel": None, "solar":None, "cell":None}

    def handle_client(self, client_socket, queue):
        """Function to handle client connections."""
        while True:
            try: 
                message = client_socket.recv(1024)

                print(f"[{str(client_socket.getpeername())}] Message: {message.decode('utf-8')}")
                client_socket.send("Message received".encode('utf-8'))

                if not message:
                    break
                
                try:
                    self.picos[message] = client_socket
                except KeyError:
                    client_socket.send(f"Message {message} is unknown".encode('utf-8'))
                                 
            except ConnectionResetError:
                break
            
            data = queue.get()

        client_socket.close()

    def start(self, queue : Queue):
        self.server.listen(6)
        print(f"Server started and listening on port {self.port}")
        
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            self.pool.submit(self.handle_client, args=(client_socket, queue))

if __name__ == "__main__":
    tcp_server = Tcp_server()
    tcp_server.start()
