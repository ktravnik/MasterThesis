import multiprocessing, time, requests

properties = ("request_time", "response_time", "request_duration", "test","timestamp",)

def map_property(status, property):
    try:   
        value = status[property]

        return str(value)
    
    except:
        return ""

def get_stats(startTime,url, timeout:int=1):
    reqTime= time.time()
    timeout_code=0
    try:
        r = requests.get(url, timeout=timeout,verify=False)
    except requests.exceptions.ReadTimeout:
        timeout_code=-1
    except Exception as e:
        print(e.args)
        timeout_code=-2
        pass
    
    respTime = time.time()
    
    if timeout_code!=0:
        duration=timeout_code
    else:
        duration = r.elapsed.total_seconds()

    
    results = {
        "request_time": reqTime - startTime, 
        "response_time": respTime - startTime,
        "request_duration": duration, 
        "test": respTime - reqTime,
        "time": time.time(),
    }

    return results

def print_status(file, startTime,url,q: multiprocessing.Queue=None, timeout:int=1):
    results = get_stats(startTime,url,timeout=timeout)

    elapsedTime = str(results["time"] - startTime)
    if q!=None:
        q.put_nowait({"probe":results})


    out = (elapsedTime,) + tuple(map(lambda k: map_property(results, k), properties))
    
    file.write(",".join(out) + "\n")
    file.flush()

def start(filename, startTime, url, q: multiprocessing.Queue=None, timeout: int=1,d: multiprocessing.Queue=None):
    file = open(filename, "w")
    
    file.write(",".join(("time_elapsed",) + properties) + "\n")
    while True:
        print_status(file, startTime, url, q, timeout)
        time.sleep(1)
        try:
            r=d.get_nowait()
        except:
            pass
            continue
        break
    file.close()
    return
