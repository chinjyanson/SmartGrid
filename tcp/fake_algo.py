import queue
import time

def driver(q):
    while True:
        data1 = {"client": "solar", "sell": 10, "buy":2, "text":"cell"}
        if not q.empty():
            message = q.get()
            print(f"Got message from a client: {message}")
        q.put(data1)
        print(f"QUEUE********************************************************************{list(q.queue)}*************************************")
        time.sleep(5)