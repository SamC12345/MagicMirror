from multiprocessing import Process, Queue
import random
import time

def putfunc(xyq):
    try:
        while True:
            xyq.put(random.randint(0,100))
            time.sleep(0.1)
    except KeyboardInterrupt:
        return
        
def getfunc(xyq):
    try:
        while True:
            print("---------")
            while not xyq.empty():
                print(xyq.get())
            time.sleep(1)
    except KeyboardInterrupt:
        return

if __name__=="__main__":
    xyq=Queue()
    Process(target = putfunc, args=(xyq,)).start()
    Process(target = getfunc, args=(xyq,)).start()