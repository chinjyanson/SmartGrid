import socket, time
import machine
from credentials import SSID, PASSWORD
import network

"""
    Functions to allow SMPS to make TCP connection to server, and send and recieve messages
"""
# code that allows rapberry pi to connect to wlan given here: https://projects.raspberrypi.org/en/projects/get-started-pico-w/2

led = machine.Pin("LED", machine.Pin.OUT)
SERVER_IP = '172.20.10.3'
SERVER_PORT = 9998
clientsocket = None

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
    
def connect_to_server():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((SERVER_IP, SERVER_PORT))
    print("connected to server")

    clientsocket.send("name".encode('utf-8'))
    time.sleep(2)
    clientsocket.settimeout(3.0)
    
if __name__ == "__main__":
    connect_to_wifi()
    connect_to_server()
    
    while(True):
        try:
            clientsocket.send(b'hello1')
            data = clientsocket.recv(1024).decode('utf-8')
            print("Data: ", data)
        except Exception as e:
            print(f"Exception: {e}")

