import socket, threading
from queue import Queue
import json, time

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('0.0.0.0', 9998))
serversocket.listen(5)

def client_listener(connection, address, q : Queue):
    print(f"New connection {connection=} {address=}")

    connection.settimeout(2.0)

    name = connection.recv(64).decode('utf-8')
    print(f"Name: {name}")

    while True:
        try:
            buf = connection.recv(64)
            if buf:
                print(f"Received: {buf}")

            if not q.empty():
                str_data = q.get()
                dict_data = json.loads(str_data)

                connection.send(str_data.encode('utf-8'))

        except Exception as e:
            print(f"Exception: {e}")

def run_server(q : Queue):
    while True:
        try:
            connection, address = serversocket.accept()
            threading.Thread(target=client_listener, args=(connection, address, q)).start()
        except KeyboardInterrupt:
            print("Closed server")

if __name__ == "__main__":
    q = Queue()
    run_server(q)