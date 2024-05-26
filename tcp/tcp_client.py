import socket
import time

# code that allows rapberry pi to connect to wlan given here: https://projects.raspberrypi.org/en/projects/get-started-pico-w/2

def connect_to_server():
    server_ip = 'laptop ip'
    server_port = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    print("Connected to server")

    try:
        while True:
            message = "Hello from Pico"
            s.send(message.encode('utf-8'))
            response = s.recv(1024)
            print(f"Received from server: {response.decode('utf-8')}")
            time.sleep(5)

    except OSError as e:
        print(f"Connection error: {e}")
        
    finally:
        s.close()

if __name__ == "__main__":
    connect_to_server()
