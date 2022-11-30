#!/usr/bin/env python3
from signal import signal, SIGINT
import os
import socket
import json
import sys
import subprocess
import time
import psutil
import sockhelper
import netutil
import re


# Define global variables
# running_command for access to the subprocess
running_command = None
# buff_size for size of chunk (reading from socket)
buff_size = 1024
# network interface name
nic_name = ""
# postprocess (download or run command)
postprocess = {}
ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def run_server(host, port):
    '''Run tcp server agent, which allows to launch DDoS'''
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Add option to be able to reuse socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    server_address = (host, port)
    print('Starting server on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print('waiting for a connection')
        try:
            connection, client_address = sock.accept()
            try:
                print('connection from', client_address)
                data = b''
                while True:
                    data = sockhelper.recv_msg(connection)
                    result = {}
                    print('Command received, processing it')
                    try:
                        command = json.loads(data)
                    except:
                        print("Could not deserialize the incoming data")
                        sockhelper.send_msg(
                            connection, 'Error: Could not deserialize the incoming data'.encode())
                        break
                    out = process_command(command)
                    result["result"] = out
                    result["agent"] = server_address
                    result_bytes = json.dumps(result).encode()
                    sockhelper.send_msg(connection, result_bytes)
                    if out == 'exit':
                        # exiting
                        print("Received exit command, exiting")
                        return

                    break
            except Exception as e:
                print("error", e.args[0])
                print("recovering")

            finally:
                # Clean up the connection
                print("Closing current connection")
                connection.close()
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting...")
            return


def process_command(cmd: dict):
    # supported commands are ping, run, status, stop, details and exit
    if cmd["command"] == 'ping':
        return int(time.time())
    elif cmd["command"] == 'run':
        return run_command(cmd)
    elif cmd["command"] == 'status':
        return status_command(cmd)
    elif cmd["command"] == 'stop':
        return stop_command(cmd)
    elif cmd["command"] == 'details':
        return details_command(cmd)
    elif cmd["command"] == 'exit':
        return 'exit'
    else:
        return "Error"


def run_command(cmd: dict):
    response = {}
    global running_command
    global nic_name
    global postprocess
    global nic_init
    global process_details
    

    if not (running_command == None or (running_command != None and running_command.poll() != None)):
        response["message"] = "AlreadyRunning"
        return response

    cmd_to_run = cmd["cmd_to_run"]
    # get file name from the path
    file = os.path.basename(cmd_to_run[0])
    # check, if the script/executable is in "scripts" subdir
    if os.access("scripts/"+file, os.X_OK):
        cmd_to_run[0] = "scripts/"+file
    # if not, try without path
    else:
        cmd_to_run[0] = file
    print(cmd_to_run)


    if "target" in cmd:
        nic_name = netutil.try_find_if(cmd["target"])
        print("Found interface", nic_name)
        stat=psutil.net_io_counters(pernic=True)
        nic_init=stat[nic_name]
    else:
        nic_name = ""
        nic_init=psutil.net_io_counters(pernic=False)
    # reset postprocess
    postprocess={}
    if "post_process" in cmd:
        postprocess = cmd["post_process"]
    # save initial network stats
    # try to start the script

    try:
        running_command = subprocess.Popen(
            cmd_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except Exception as e:
        response["message"] = "Failed"
        response["error"] = e.args[0]
        return response

    response["message"] = "Started"
    response["PID"] = running_command.pid
    process_details = psutil.Process(running_command.pid)

    return response


def get_process_details() -> dict:
    global running_command
    if running_command == None:
        return None
    process_details = {}
    process_details["pid"] = running_command.pid
    process_details["returncode"] = running_command.poll()
    if running_command.poll() == None:
        return process_details

    process_details["stdout"] = running_command.stdout.read().decode()
    process_details["stdout"] = ansi_escape.sub('', process_details["stdout"])
    process_details["stderr"] = running_command.stderr.read().decode()
    process_details["stderr"] = ansi_escape.sub('', process_details["stderr"])

    if "cmd" in postprocess:
        print("TODO run the command")
    if "download" in postprocess:
        download = {}
        for file in postprocess["download"]:
            print("downloading", file)
            try:
                fs = open(file, mode='r')
                # read all lines at once
                all_of_it = fs.read()
                download[file]=all_of_it
            except:
                print("Error reading file")
            # close the file
            finally:
                fs.close()
        process_details["downloads"] = download
    return process_details


def details_command(cmd: dict):
    response = {}
    resp = get_process_details()
    if resp == None:
        response["message"] = "NoData"
        return response
    if resp["returncode"] == None:
        response["message"] = "IsRunning"
        return response
    else:
        response["message"] = "Finished"
    response["process_details"] = resp
    return response


def stop_command(cmd: dict):
    response = {}
    global running_command
    if running_command == None:
        response["message"] = "NeverRunning"
        return response
    if running_command.poll() == None:
        running_command.send_signal(SIGINT)
        time.sleep(0.5)
        if running_command.poll() == None:
            running_command.terminate()
            time.sleep(1)
            if running_command.poll() == None:
                running_command.kill()
        msg = "Terminated"
    else:
        msg = "NotRunning"
    response["message"] = msg
    return msg


def status_per_connection(input: list) -> dict:
    per_conn = {}
    for item in input:
        if item[5] in per_conn:
            per_conn[item[5]] += 1
        else:
            per_conn[item[5]] = 1

    return per_conn


def get_stats():
    global running_command
    global nic_name
    global process_details
    global nic_init
    current_stats = {}
    if running_command.poll() != None:
        return current_stats

    current_stats["timestamp"] = int(time.time())
    current_stats["cpu"] = process_details.cpu_percent()
    current_stats["memory"] = process_details.memory_percent()
    current_stats["connections"] = status_per_connection(
        process_details.connections())
    if nic_name == "":
        curr_nic = list(psutil.net_io_counters(pernic=False))
    else:
        stat = psutil.net_io_counters(pernic=True)
        curr_nic = list(stat[nic_name])
    
    for i in range(len(curr_nic)):
        curr_nic[i] -= nic_init[i]
    current_stats["nicstat"]=tuple(curr_nic)
    print("stat for", nic_name, current_stats["nicstat"])
    return current_stats


def status_command(cmd: dict):
    response = {}
    global running_command
    if running_command == None:
        response["message"] = "NeverRunning"
    if running_command.poll() == None:
        response["message"] = "IsRunning"
        response["current_stats"] = get_stats()
    else:
        response["message"] = "NotRunning"
    return response


if __name__ == "__main__":

    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
    except:
        host = "localhost"
        port = 10050
    run_server(host, port)
