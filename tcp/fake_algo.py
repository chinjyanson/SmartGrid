import queue
import time

def driver(q):
    while True:
        data1 = {"client": "solar", "sell": 10, "buy":2, "text":"cell"}
        if not q.empty():
            message = q.get()
            print(f"Got message from a client: {message}")
            # Add your processing logic here
            # Optionally, put response back into the queue
        q.put(data1)
        print(f"QUEUE********************************************************************{list(q.queue)}*************************************")
        time.sleep(5)