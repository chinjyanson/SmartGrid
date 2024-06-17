import socket
import threading
import json
from queue import Queue

clients = {}

# Function to handle each client connection
def handle_client(client_socket, addr, client_name, q):
    print(f"Client {client_name} connected from {addr}")

    while True:
        try:
            if not q.empty():
                data = q.get()

                if any([client == client_name for client in data['client']]):
                    client_socket.sendall(json.dumps(data).encode('utf-8'))
                    data['client'] = client_name # set to specific client name
                    print(f"Sent {data} to {data['client']}")
                    str_data = json.dumps(data).encode('utf-8')
                    client_socket.sendall(str_data)

            #print(f"************************************TCP Queue: {list(q.queue)}")

            # Receive data from client and put it on the queue
            #data = client_socket.recv(2048)
            #if data:
            #    str_data = data.decode('utf-8')
            #   dict_data = json.loads(str_data)
            #    q.put(dict_data)
            #    print(f"Received from {client_name} and added to queue: {dict_data}")

        except Exception as e:
            #print(f"Error handling client {client_name}: {e}")

            #print(f"Client {client_name} disconnected")
            #client_socket.close()

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

if __name__ == "__main__":
    q = Queue()
    start_server('0.0.0.0', 5555, q)
