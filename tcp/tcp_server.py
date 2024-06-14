import socket
import selectors
import json
from queue import Queue
from threading import Lock
from functools import partial

sel = selectors.DefaultSelector()
picos = {"flywheel": None, "solar": None, "cell": None}
message_queues = {name: Queue() for name in picos}
lock = Lock()

def accept(sock, mask, q):
    conn, addr = sock.accept()
    print(f'Accepted connection from {addr}')
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, partial(read_initial, q=q))

def close_conn(conn):
    try:
        print(f'Closing connection to {conn.getpeername()}')
    except Exception as e:
        print(f'Error getting peer name: {e}')
    sel.unregister(conn)
    conn.close()

def read_initial(conn, mask, q):
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        print(f'Initial read data: "{data}"')
        if not data:
            raise ValueError("No data received")
        name = data.strip()
        if name in picos:
            picos[name] = conn
            sel.modify(conn, selectors.EVENT_READ, partial(read, q=q, pico_name=name))
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

def read(conn, mask, q, pico_name):
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        print(f'Received data from {pico_name}: "{data}"')
        if data:
            process_message(data, conn, q, pico_name)
        else:
            close_conn(conn)
    except BlockingIOError:
        print("BlockingIOError during read, will retry")
    except socket.timeout:
        close_conn(conn)
    except Exception as e:
        print(f"Error during read: {e}")
        close_conn(conn)

def write(conn, mask, q, pico_name):
    with lock:
        if not q.empty():
            try:
                message = q.get_nowait()
                conn.send(message.encode('utf-8'))
                print(f"Sent to {pico_name}: {message}")
            except socket.error as e:
                print(f"Error sending data: {e}")
                close_conn(conn)
        sel.modify(conn, selectors.EVENT_READ, partial(read, q=q, pico_name=pico_name))

def process_message(data, conn, q, pico_name):
    try:
        message = json.loads(data)
        response = {"status": "received", "name": pico_name, "timestamp": message["timestamp"]}
        q.put(json.dumps(response))
        print(f"Processed and queued response for {pico_name}: {response}")
        sel.modify(conn, selectors.EVENT_WRITE, partial(write, q=q, pico_name=pico_name))
    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}, raw data: {data}")

def run_server(host, port, q: Queue):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen()
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, partial(accept, q=q))

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
    q = Queue()
    run_server('0.0.0.0', 9998, q)
