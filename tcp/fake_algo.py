import queue
import time
import random

def driver(q):
    while True:
        data1 = {"client": ["load", "load1"], "power":random.uniform(0, 1.5)}
        data2 = {"client": ["bidirectional"], "power":random.uniform(0, 1.5)}
        if(q.empty()):
            q.put(data1)
        print(f"QUEUE********************************************************************{list(q.queue)}*************************************")
        time.sleep(5)