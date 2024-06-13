import socket
import threading
import time
import json
from credentials import SSID, PASSWORD
import machine, network

# code that allows rapberry pi to connect to wlan given here: https://projects.raspberrypi.org/en/projects/get-started-pico-w/2

led = machine.Pin("LED", machine.Pin.OUT)

def connect_to_wifi():
    """
        Connect the PICO to wifi
    """
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print("Connected with ip", ip)

class Tcp_client:
    def __init__(self, host='172.20.10.3', port=9999, client_name='solar'):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10) # seconds

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            self.socket.sendall(self.client_name.encode('utf-8'))
        except Exception as exc:
            print(f"Connection to server failed because of {exc}")

    def send_data(self, data):
        try:
            message = json.dumps(data)
            self.socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send data: {e}")

    def receive_data(self):
        while True:
            try:
                response = self.socket.recv(1024).decode('utf-8')
                if response:
                    print(f"Received from server: {response}")
                else:
                    break
            except Exception as e:
                print(f"Failed to receive data: {e}")
        
    def start_receiving(self):
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.daemon = True
        receive_thread.start()

    def close(self):
        self.socket.close()
        print("Connection closed")

if __name__ == "__main__":
    name = "cell"
    client = Tcp_client(client_name=name)
    connect_to_wifi()
    client.connect()
    
    time.sleep(2)
    
    client.start_receiving()

    # Example of sending data to the server
    try:
        while True:
            data = {
                'name': name,
                'value': 1234,
                'timestamp': time.time()
            }
            client.send_data(data)
            time.sleep(5)  
    except KeyboardInterrupt:
        client.close()

