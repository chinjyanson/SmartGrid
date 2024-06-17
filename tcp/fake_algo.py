import queue
import time

def driver(q):
    while True:
        data1 = {"client": "load", "power":13/20}
        data2 = {"client": "bidirectional", "buysell":-10, "storage":23}
        if not q.empty():
            message = q.get()
            print(f"Got message from a client: {message}")
        q.put(data1)
        print(f"QUEUE********************************************************************{list(q.queue)}*************************************")
        time.sleep(5)