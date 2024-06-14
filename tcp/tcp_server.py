import socket
from queue import Queue 
from threading import Lock
import selectors
import json

# Initialize the default selector
sel = selectors.DefaultSelector()
picos = {"flywheel": None, "solar":None, "cell":None}  

def accept(sock, mask):
    conn, addr = sock.accept()  
    print(f'Accepted connection from {addr}')

    name = conn.recv(1024).decode('utf-8')

    if(name == "cell" or name == "solar" or name == "flywheel"):
        print("Pico has name ", name)
        picos[name] = conn
    else:
        print(f"Pico name {name} is unknown")

    conn.settimeout(6) # seconds

    sel.register(conn, selectors.EVENT_WRITE, write) 

def close_conn(conn):
    print(f'Closing connection to {conn.getpeername()}')
    sel.unregister(conn)  # Unregister the connection
    conn.close()  # Close the connection

def read(conn, mask):
    print("Reading data from client")
    try:
        data = conn.recv(1024)  # Read data from the connection
        if data:
            print(f'Received {data} from {conn.getpeername()}')
            sel.modify(conn, selectors.EVENT_WRITE, write)

    except Exception as e:
        print(e)
        close_conn(conn)

def write(conn, mask, q : Queue):
    print("Writing data to client")
    with Lock():
        if (not q.empty()):
            str_data = q.get()
            dict_data = json.loads(str_data)
            print(f"Sending {dict_data} to relevant client")

            if(picos[dict_data["name"]] == conn):
                try:
                    conn.send(str_data.encode('utf-8'))
                except socket.timeout:
                    close_conn(conn)

    sel.modify(conn, selectors.EVENT_READ, read) 

def run_server(host, port, q : Queue):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen()
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, accept)  # Register the server socket for accept events

    print(f'Server listening on {host}:{port}')
    try:
        while True:
            events = sel.select()  
            for key, mask in events:
                callback = key.data  # Get the callback function

                if(mask == selectors.EVENT_WRITE):
                    callback(key.fileobj, mask, q) 
                else:
                    callback(key.fileobj, mask) 

    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        sel.close()


if __name__ == "__main__":
    q = Queue()

    run_server('0.0.0.0', 9999, q)
