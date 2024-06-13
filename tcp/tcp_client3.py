import socket
import time
import network
import machine
from credentials import SSID, PASSWORD
import ujson

led = machine.Pin("LED", machine.Pin.OUT)

class Tcp_client:
    def __init__(self, host, port, client_name, blocking=True):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.socket = None
        self.is_connected = False
        self.blocking = blocking

    def connect(self):
        try:
            if self.socket:
                self.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(self.blocking)
            if self.blocking:
                self.socket.settimeout(10)  # Add timeout for blocking mode
            print(f"Connecting to server {self.host}:{self.port}")
            self.socket.connect((self.host, self.port))
            self._finalize_connection()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.socket = None
            self.is_connected = False

    def _finalize_connection(self):
        try:
            self.socket.send(self.client_name.encode('utf-8'))
            print("Connected to server")
            self.is_connected = True
        except Exception as e:
            print(f"Error finalizing connection: {e}")
            self.close()
            self.is_connected = False

    def send_data(self, data):
        if not self.socket or not self.is_connected:
            print("Not connected to server")
            return
        try:
            json_data = ujson.dumps(data)
            self.socket.send(json_data.encode('utf-8'))
            print(f"Sent data: {json_data}")
        except Exception as e:
            print(f"Error sending data: {e}")
            self.close()
            self.is_connected = False

    def receive_data(self):
        if not self.socket or not self.is_connected:
            print("Not connected to server")
            return None
        try:
            data = self.socket.recv(1024)
            if data:
                received_data = ujson.loads(data.decode('utf-8'))
                print(f"Received data: {received_data}")
                return received_data
            else:
                print("Received no data, closing connection")
                self.close()
                self.is_connected = False
        except Exception as e:
            print(f"Error receiving data: {e}")
            self.close()
            self.is_connected = False
        return None

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            print("Connection closed")
            self.is_connected = False

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print("Connected with IP", ip)

