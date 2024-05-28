import socket
from threading import Thread

connected_clients = []

def handle_client(client_socket):
    """Function to handle client connections."""
    while True:
        try: 
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"[{str(client_socket.getpeername())}] Received: {message.decode('utf-8')}")
            client_socket.send("Message received".encode('utf-8'))
        except ConnectionResetError:
            break
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9999
    server.bind(('0.0.0.0', port))
            
    server.listen(6)
    print(f"Server started and listening on port {port}")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = Thread(target=handle_client, args=(client_socket, ))
        client_handler.start()

if __name__ == "__main__":
    start_server()
