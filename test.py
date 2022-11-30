import psutil
from time import sleep 


def setup():
    PID=5161
    global p
    p=psutil.Process(PID)
    

def run():
    while True:
        print("cpu",p.cpu_percent())
        print("memory",p.memory_percent())
        print("memory",p.memory_info())
        sleep(1)

if __name__ == "__main__":
    setup()
    run()