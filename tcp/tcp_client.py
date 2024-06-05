import socket
import time
import network
import machine

"""
    Functions to allow SMPS to make TCP connection to server, and send and recieve messages
"""
# code that allows rapberry pi to connect to wlan given here: https://projects.raspberrypi.org/en/projects/get-started-pico-w/2
ssid = 'Yuh'
password = 'chinjyanson'

led = machine.Pin("LED", machine.Pin.OUT)

def connect():
    """
        Connect the PICO to wifi
    """
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print("Connected with ip", ip)

def connect_to_server():
    """
        Connect the PICO to server (laptop)
    """
    server_ip = '192.168.241.163'
    server_port = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    print("Connected to server")

    return s

def get_message(socket):
    """
        Sends message to socket, and returns message from server
    """
    message = "Hello from Pico"  # send particular message beased on which PICO this one is
    socket.send(message.encode('utf-8'))
    response = socket.recv(1024)
    # print(f"Received from server: {response.decode('utf-8')}")

    return response.decode('utf-8')

if __name__ == "__main__":
    led.toggle()
    connect()
    connect_to_server()

    while True:
        get_message()

