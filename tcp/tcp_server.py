import socket
import selectors
import json
from queue import Queue
from threading import Lock

sel = selectors.DefaultSelector()
picos = {"flywheel": None, "solar": None, "cell": None}
message_queues = {name: Queue() for name in picos}

def accept(sock, mask):
    conn, addr = sock.accept()
    print(f'Accepted connection from {addr}')
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read_initial)

def close_conn(conn):
    try:
        print(f'Closing connection to {conn.getpeername()}')
    except Exception as e:
        print(f'Error getting peer name: {e}')
    sel.unregister(conn)
    conn.close()

def read_initial(conn, mask):
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        print(f'Initial read data: "{data}"')
        if not data:
            raise ValueError("No data received")
        name = data.strip()
        if name in picos:
            picos[name] = conn
            sel.modify(conn, selectors.EVENT_READ, read)
            print(f"Registered client {name}")
        else:
            print(f"Unknown client name: {name}")
            close_conn(conn)
    except BlockingIOError:
        print("BlockingIOError during initial read, will retry")
    except ValueError as e:
        print(f"Error: {e}")
        close_conn(conn)
    except Exception as e:
        print(f"Error during initial read: {e}")
        close_conn(conn)

def read(conn, mask):
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        print(f'Received data: "{data}"')
        if data:
            process_message(data, conn)
        else:
            close_conn(conn)
    except BlockingIOError:
        print("BlockingIOError during read, will retry")
    except socket.timeout:
        close_conn(conn)
    except Exception as e:
        print(f"Error during read: {e}")
        close_conn(conn)

def write(conn, mask):
    pico_name = next((name for name, c in picos.items() if c == conn), None)
    if pico_name:
        with Lock():
            if not message_queues[pico_name].empty():
                msg = message_queues[pico_name].get()
                try:
                    conn.send(json.dumps(msg).encode('utf-8'))
                    print(f"Sent message to {pico_name}: {msg}")
                except BlockingIOError:
                    print("BlockingIOError during write, will retry")
                except Exception as e:
                    print(f'Error sending data: {e}')
                    close_conn(conn)
    sel.modify(conn, selectors.EVENT_READ, read)

def process_message(data, conn):
    try:
        message = json.loads(data)
        pico_name = message.get('name')
        if pico_name in picos:
            message_queues[pico_name].put(message)
            print(f"Queued message for {pico_name}: {message}")
            sel.modify(conn, selectors.EVENT_WRITE, write)
        else:
            print(f"Received message for unknown pico: {pico_name}")
    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")
        print(f"Raw data received: {data}")

def run_server(host, port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen()
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, accept)

    print(f'Server listening on {host}:{port}')
    try:
        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        sel.close()
        server_sock.close()

if __name__ == "__main__":
    run_server('0.0.0.0', 9998)
