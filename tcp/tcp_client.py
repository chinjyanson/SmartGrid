import socket
import time
import network
import machine
from credentials import SSID, PASSWORD

"""
    Functions to allow SMPS to make TCP connection to server, and send and recieve messages
"""
# code that allows rapberry pi to connect to wlan given here: https://projects.raspberrypi.org/en/projects/get-started-pico-w/2

led = machine.Pin("LED", machine.Pin.OUT)

def connect():
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

def connect_to_server(name):
    """
        Connect the PICO to server (laptop)
    """
    server_ip = '172.20.10.2'
    server_port = 9998
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    print("Connected to server")
    
    s.send(name.encode('utf-8'))

    return s

def get_message(socket):
    """
        Returns message from server
    """
    #message = "Hello from Pico"  # send particular message beased on which PICO this one is
    #socket.send(message.encode('utf-8'))
    response = socket.recv(1024)
    # print(f"Received from server: {response.decode('utf-8')}")

    return response.decode('utf-8')

if __name__ == "__main__":
    led.toggle()
    connect()
    socket = connect_to_server("cell")

    while True:
        received = get_message(socket)
        print(f"Received {received} from server")


