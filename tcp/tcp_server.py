import socket
import threading
from multiprocessing import  Queue
import json
import time
# from queue import Queue

clients = {}

# Function to handle each client connection
def handle_client(client_socket, addr, client_name, q):
    print(f"Client {client_name} connected from {addr}")

    while True:
        try:
            got = False
            while not got:
                data = q.get()

                if data['client'] == client_name:
                    client_socket.sendall(json.dumps(data).encode('utf-8'))
                    print(f"Sent {data} to {client_name}")
                    str_data = json.dumps(data).encode('utf-8')
                    client_socket.sendall(str_data)
                    got = True
                elif data["client"] in clients:
                    q.put(data)

        except Exception as e:
            print(f"Error handling client {client_name}: {e}")
            #print(f"Client {client_name} disconnected")
            #client_socket.close()
            break
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            break

# Function to start the server and listen for clients
def start_server(host, port, q):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_name = client_socket.recv(1024).decode('utf-8')  # Expecting the client to send its name first
        clients[client_name] = client_socket
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, client_name, q))
        client_thread.daemon = True
        client_thread.start()
        #client_process = Process(target=handle_client, args=(client_socket, addr, client_name, q, ))
        #client_process.start()

if __name__ == "__main__":
    q = Queue()
    start_server('0.0.0.0', 5555, q)
