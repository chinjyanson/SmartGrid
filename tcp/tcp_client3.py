import socket
import time
import network
import machine
import ujson
import select
import errno
from credentials import SSID, PASSWORD

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
        self._connect_to_server()

    def _connect_to_server(self):
        try:
            if self.socket:
                self.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(0)  # Non-blocking mode
            print(f"Connecting to server {self.host}:{self.port}")
            try:
                self.socket.connect((self.host, self.port))
            except OSError as e:
                if e.args[0] not in [errno.EINPROGRESS, errno.EALREADY]:
                    raise
            if self._wait_for_connection():
                self._finalize_connection()
            else:
                raise Exception("Connection timed out")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.socket = None
            self.is_connected = False

    def _wait_for_connection(self, timeout=10):
        for _ in range(timeout):
            _, ready_to_write, _ = select.select([], [self.socket], [], 1)
            if ready_to_write:
                return True
            time.sleep(1)
        return False

    def _finalize_connection(self):
        try:
            self.socket.send(self.client_name.encode('utf-8'))
            print("Connected to server")
            self.is_connected = True
        except Exception as e:
            print(f"Error finalizing connection: {e}")
            self.close()
            self.is_connected = False

    def maintain_connection(self):
        if not self.socket or not self.is_connected:
            print("Not connected to server, attempting to reconnect...")
            self._connect_to_server()

    def send_data(self, data):
        if not self.socket or not self.is_connected:
            print("Not connected to server")
            self.maintain_connection()
            return
        try:
            json_data = ujson.dumps(data)
            _, ready_to_write, _ = select.select([], [self.socket], [], 1)
            if ready_to_write:
                self.socket.send(json_data.encode('utf-8'))
                print(f"Sent data: {json_data}")
            else:
                raise Exception("Socket not ready for writing")
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                print(f"EAGAIN, retrying send...")
                time.sleep(1)  # Backoff before retrying
                self.send_data(data)
            else:
                print(f"Error sending data: {e}")
                self.close()
                self.is_connected = False
                self.maintain_connection()
        except Exception as e:
            print(f"Error sending data: {e}")
            self.close()
            self.is_connected = False
            self.maintain_connection()

    def receive_data(self):
        if not self.socket or not self.is_connected:
            print("Not connected to server")
            self.maintain_connection()
            return None
        try:
            ready_to_read, _, _ = select.select([self.socket], [], [], 1)
            if ready_to_read:
                data = self.socket.recv(1024)
                if data:
                    received_data = ujson.loads(data.decode('utf-8'))
                    print(f"Received data: {received_data}")
                    return received_data
                else:
                    print("Received no data, closing connection")
                    self.close()
                    self.is_connected = False
            else:
                raise Exception("Socket not ready for reading")
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                print(f"EAGAIN, retrying receive...")
                time.sleep(1)  # Backoff before retrying
                return self.receive_data()
            else:
                print(f"Error receiving data: {e}")
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

