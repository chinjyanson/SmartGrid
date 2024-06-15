import network
import socket
import json
import _thread
import machine
import utime
from credentials import SSID, PASSWORD

# Function to connect to Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to Wi-Fi...", end="")
    
    # Wait for the connection to complete
    while not wlan.isconnected():
        print(".", end="")
        utime.sleep(1)
    
    print(" Connected!")
    print("Network configuration:", wlan.ifconfig())

# Function to receive data from the server
def receive_from_server(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            received_json = data.decode('utf-8')
            parsed_data = json.loads(received_json)
            print(f"Received from server: {parsed_data}")
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Function to send dummy data to the server
def send_to_server(client_socket, data):
    while True:
        # Generate dummy data with client name
        try:
            client_socket.sendall(json.dumps(data).encode('utf-8'))
            print(f"Sent to server: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")
        
        utime.sleep(5)  # Wait 5 seconds before sending the next dummy data


# Function to start the client
def start_client(server_host, server_port, client_name, ssid, password, data):
    # Connect to Wi-Fi
    connect_wifi(ssid, password)
    
    # Create a socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    print(client_name.encode('utf-8'))
    client_socket.sendall(client_name.encode('utf-8'))  # Send the client's name to the server
    utime.sleep(3)

    # Start threads for sending and receiving data
    _thread.start_new_thread(receive_from_server, (client_socket,))

    return client_socket

if __name__ == "__main__":
    server_host = '192.168.90.7'  # Replace with your server's IP address
    server_port = 5555
    client_name = 'Client1'  # Replace with your client name
    data = None
    
    client_socket = start_client(server_host, server_port, client_name, SSID, PASSWORD)
    send_to_server(client_socket, data)

