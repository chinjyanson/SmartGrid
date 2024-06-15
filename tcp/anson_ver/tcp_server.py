import socket
import threading
import json
from queue import Queue

clients = {}



# Function to handle each client connection
def handle_client(client_socket, addr, client_name, queue):
    print(f"Client {client_name} connected from {addr}")

    while True:
        try:
            # Receive data from client and put it on the queue
            data = client_socket.recv(1024)
            if not data:
                break
            
            received_json = data.decode('utf-8')
            parsed_data = json.loads(received_json)
            queue.put((client_name, parsed_data))
            print(f"Received from {client_name} and added to queue: {parsed_data}")

            # Check the queue and send data to the client if available
            while not queue.empty():
                recipient_name, message = queue.get()
                if recipient_name == client_name:
                    json_data = json.dumps(message).encode('utf-8')
                    client_socket.sendall(json_data)
                    print(f"Sent to {client_name}: {message}")

        except Exception as e:
            print(f"Error handling client {client_name}: {e}")
            break

    print(f"Client {client_name} disconnected")
    client_socket.close()
    del clients[client_name]

# Function to start the server and listen for clients
def start_server(host, port, queue):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        if not q.empty():
            data1 = {"toClient": "solar", "sell":True, "buy":False, "name":"cell"}
            data2 = {"toClient": "solar", "sell":False, "buy":False, "name":"load"}
            queue.put(data1)
            queue.put(data2)
            queue.task_done()
        client_socket, addr = server_socket.accept()
        client_name = client_socket.recv(1024).decode('utf-8')  # Expecting the client to send its name first
        clients[client_name] = client_socket
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, client_name, queue))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    q = Queue()
    start_server('0.0.0.0', 5555, q)
