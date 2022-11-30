#!/usr/bin/env python3

import tkinter as tk
from tkinter import *
import multiprocessing
import threading
import os
import glob
import json
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from traceback import print_tb
from turtle import color, width
import webbrowser
import master
import sys
import time
import respTime

#from PIL import Image, ImageTk

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text='widget info'):
        self.waittime = 500  # milliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


def human_readable_size(size, decimal_places=3):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"

# export form valaues to the json
def export_values():
    values = []
    export = {"desc": main_combo.get(), "values": values,
              "agent_values": {
        "warming_up_interval": warming_up_interval.get(),
        "stat_interval": stat_interval.get(),
        "all_agents": all_agents.get(),
        "probe_url": probe_url.get(),
    }}

    for item in varList:
        values.append(item.get())
    fs = filedialog.asksaveasfile(defaultextension=".json", filetypes=(
        ("JSON file", "*.json"), ("All Files", "*.*")), initialdir=".")
    if fs == None:
        return
    export_file = open(fs.name, "w")
    export_file.write(json.dumps(export))
    export_file.close()

# import json file to the form values
def import_values():
    fs = filedialog.askopenfile(defaultextension="*.json", filetypes=(
        ("JSON file", "*.json"), ("All Files", "*.*")), initialdir=".")
    try:
        j = json.load(fs)
        i = main_list.index(j["desc"])
    except:
        messagebox.showinfo(
            message="Could not read the file {} or it is not correct format".format(fs.name))
        return

    main_combo.current(i)
    populate_frame(discovery_list[main_list[i]], main_frame)
    k = 0
    for item in varList:
        item.set(j["values"][k])
        k += 1
    if "agent_values" in j:
        all_agents.set(j["agent_values"]["all_agents"])
        warming_up_interval.set(j["agent_values"]["warming_up_interval"])
        stat_interval.set(j["agent_values"]["stat_interval"])
        probe_url.set(j["agent_values"]["probe_url"])


def change_theme():
    # NOTE: The theme's real name is azure-<mode>
    if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
        # Set light theme
        root.tk.call("set_theme", "light")
    else:
        # Set dark theme
        root.tk.call("set_theme", "dark")

# discovering scripts
def discover_script(script):
    try:
        json_file = open(script)
    except:
        print("File could not be read", script)
        return
    try:
        j = json.load(json_file)
    except:
        print("JSON is not valid or file could not be read", script)
        return
    j["script"] = script
    return j


# Find scripts and return the list of them
def find_scripts() -> list:
    # Find scripts
    print("Searching for scripts ...")
    scripts_dir = f"{os.path.dirname(os.path.realpath(__file__))}/scripts/"
    scripts = glob.glob(f"{scripts_dir}*.json")
    print(f"Scripts found: {scripts}")
    return scripts

# get description key 
def get_description(j):
    return j['description']

# populate vars array
def populate_vars(v: dict, frame: ttk.Frame):
    lv = []
    i = 0
    for p in v:
        val = None
        if "default" in p:
            val = p["default"]
        if "value" in p:
            val = p["value"]
        if p["type"] == "numeric":
            lv.append(StringVar(frame, value=val))
        elif p["type"] == "string":
            lv.append(StringVar(frame, value=val))
        elif p["type"] == "options":
            lv.append(StringVar(frame, value=val))
        i = i+1
    return lv

# populate frame based on description
def populate_frame(input: dict, frame: ttk.Frame):
    # icon load
    global submit_run
    global cancel_run
    global varList
    global s
    text_font_icon = f"{os.path.dirname(os.path.realpath(__file__))}/img/icons8-info-24.png"
    _photo = tk.PhotoImage(file=text_font_icon)
    # print(input)
    for widget in frame.winfo_children():
        widget.destroy()
    s = json.loads(json.dumps(input))

    
    # Create a frame for the canvas with non-zero row&column weights
    frame_canvas = ttk.Frame(frame)
    frame_canvas.grid(row=0, column=0, pady=10, sticky='nesw')
    frame_canvas.grid_rowconfigure(0, weight=2)
    frame_canvas.grid_columnconfigure(0, weight=2)

    # Add a canvas in that frame
    canvas = tk.Canvas(frame_canvas)
    canvas.grid(row=0, column=0, sticky="news")

    # Link a scrollbar to the canvas
    vsb = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    canvas.configure(yscrollcommand=vsb.set)

    # Create a frame to contain the buttons
    frame_buttons = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_buttons, anchor='nw')

    desc = ttk.Label(frame_buttons, text=s["description"])
    if "detail_description" in s:
        detail_desc.configure(text=s["detail_description"])
    else:
        detail_desc.configure(text="")
    desc.grid(row=0, column=0, padx=10, pady=10, sticky="nesw")
    desc.grid_rowconfigure(0, weight=1)
    desc.grid_columnconfigure(0, weight=1)

    varList = populate_vars(s['params'], frame_buttons)
    i = 0
    for p in s['params']:
        if "target" in p:
            s["target"] = i
        if "label" in p:
            l = ttk.Label(frame_buttons, text=p["label"],
                          image=_photo, compound=tk.RIGHT)

            l.image = _photo
            l.grid(row=1+i, column=0, padx=10, pady=10, sticky="nesw")
            l.grid_rowconfigure(1+i, weight=1)
            l.grid_columnconfigure(0, weight=1)
            button1_ttp = CreateToolTip(l, text=p["description"])
        if p["type"] == "options":
            o = p["options"]
            t = tk.OptionMenu(frame_buttons, varList[i], *o)
            varList[i].set(o[0])
            t.grid(row=1+i, column=1, padx=10, pady=10)
            t.grid_rowconfigure(1+i, weight=1)
            t.grid_columnconfigure(1, weight=1)
        else:
            if "value" in p:
                st = 'readonly'
            else:
                st = 'normal'
            t = ttk.Entry(frame_buttons, textvariable=varList[i], state=st)

            t.grid(row=1+i, column=1)
        i = i + 1
    # Update buttons frames idle tasks to let tkinter calculate buttons sizes
    frame_buttons.update_idletasks()
    #frame_canvas.config(width=)
    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas.bbox("all"))

# run the attack
def run_script_with_param(command: list, target: str, post_process: dict, test_name: str):
    global result_queue
    global status_queue
    global execute_script
    global stat_interval
    global warming_up_interval
    global cmb_agents
    global all_agents
    global path
    global resptime

    print(command)
    # def run_agents(agent_list:list,status_queue: multiprocessing.Queue,agg_results_queue: multiprocessing.Queue, task: dict,results_path: str,status_period: int, start_period: int):
    agentlist = []
    if all_agents.get() <= 1:
        # run on the currently chosen agent
        agentlist.append((configuration["agent_list"][cmb_agents.current(
        )][0], configuration["agent_list"][cmb_agents.current()][1]))
    else:
        i = 1
        for item in configuration["agent_list"]:
            agentlist.append((item[0], item[1]))
            if i >= all_agents.get():
                break
            i += 1

    # create dir
    timestr = time.strftime("%Y%m%d-%H%M%S")
    path = "results/" + test_name + "/" + timestr
    path = path.replace(" ", "_")
    os.makedirs(path)

    si = stat_interval.get()
    if si < 1:
        stat_interval.set(1)
        si = 1

    result_queue = multiprocessing.Queue()
    status_queue = multiprocessing.Queue()
    cmd = {"command": "run", "cmd_to_run": command}
    if target != None:
        cmd["target"] = target
    if post_process != None:
        cmd["post_process"] = post_process
    execute_script = threading.Thread(target=master.run_agents, args=(
        (agentlist, status_queue, result_queue, cmd, path, warming_up_interval.get(), si)))
    execute_script.start()
    execute_results = threading.Thread(
        target=process_results, args=((result_queue, stats_frame)))
    execute_results.start()
    url = probe_url.get()
    if url != "":
        startTime = time.time()
        resptime = threading.Thread(target=respTime.start, args=(
            path + "/response.csv", startTime, url, result_queue, 3, status_queue))
        resptime.start()
    else:
        resptime = None

# clear form values after the attack finished
def reset_stats():
    mem_entry.configure(text="")
    cpu_entry.configure(text="")
    agentcount_entry.configure(text="")
    established_entry.configure(text="")
    syncsent_entry.configure(text="")
    bytesent_entry.configure(text="")
    bytercv_entry.configure(text="")
    packetsent_entry.configure(text="")
    packetrcv_entry.configure(text="")
    probe_entry.configure(text="")

# process results, coming from the queue
def process_results(result_queue: multiprocessing.Queue, frame: tk.Frame):
    while True:
        res = result_queue.get()
        if res == "DONE":
            interrupt_the_script(fromButton=False)
            return
        if "message" in res:
            agentstatus_entry.configure(text=res["message"])
            continue
        if "probe" in res:
            print(res)
            duration = res["probe"]["request_duration"]
            if duration < 0:
                duration = "Probe URL doesn't respond"
            probe_entry.configure(text=duration)
            continue
        mem_entry.configure(text="{:.3f}".format(res["memory"]))
        cpu_entry.configure(text="{:.3f}".format(res["cpu"]))
        agentcount_entry.configure(text=res["running_agents"])
        established_entry.configure(text=res["connections_established"])
        syncsent_entry.configure(text=res["connections_sync_sent"])
        bytesent_entry.configure(
            text=human_readable_size(res["nic_bytes_sent"]))
        bytercv_entry.configure(
            text=human_readable_size(res["nic_bytes_received"]))
        packetsent_entry.configure(text=res["nic_packet_sent"])
        packetrcv_entry.configure(text=res["nic_packet_received"])

# so far unused
def disable_all(parent: tk.Frame, exception: list):
    for w in parent.winfo_children():
        if w.winfo_name in exception:
            continue
        w.configure(state="disabled")


def run_the_script(vars: list, input: dict, *toDisable):
    i = 0
    notDisable = []
    target = None
    post_process = None
    cmd = [input["script"][:-5]]
    if "post_process" in input:
        post_process = input["post_process"]
    for item in input["params"]:
        s = str(vars[i].get())
        if "target" in item:
            target = s
        if "prefix" in item and s != "":
            cmd.append(item["prefix"])
        try:
            required = item["required"]
        except:
            required = False

        if s == "" and required:
            agentstatus_entry.configure(
                text="Could not start the script. Parameter '{}' is empty and it is required".format(item["label"]))
            return
        if s != "":
            cmd.append(s)
        i = i + 1
    global submit_run
    global cancel_run
    submit_run.configure(state="disabled")
    cancel_run.configure(state="normal")
    # for dis in toDisable:
    #     disable_all(dis, notDisable)
    run_script_with_param(
        cmd, target=target, post_process=post_process, test_name=input["description"])

    # for dis in toDisable:
    #     dis['state'] = 'active'


def interrupt_the_script(fromButton=True):
    global submit_run
    global cancel_run
    global status_queue
    global result_queue
    global resptime
    int_text = "Attack on all bots is about to finish, please wait..."
    if fromButton:
        int_text = "Interrupting the attack by user request, please wait..."
    agentstatus_entry.configure(text=int_text)
    result_queue.put("DONE", block=True, timeout=5)
    status_queue.put("DONE", block=True, timeout=5)
    if resptime != None:
        status_queue.put("DONE", block=True, timeout=5)
    if fromButton:
        return
    try:
        submit_run.configure(state="normal")
        cancel_run.configure(state="disabled")
        reset_stats()
    except:
        pass
    time.sleep(stat_interval.get())
    agentstatus_entry.configure(text="Finished")
    open_url = messagebox.askquestion(message="Finished. Details of the last attack you can find in the directory: \n{}\nDo you want to open browser now?".format(
        os.path.dirname(os.path.realpath(__file__))+"/"+path))
    if open_url == "yes":
        webbrowser.open(
            "file://"+os.path.dirname(os.path.realpath(__file__))+"/"+path)


##### MAIN #######
# discovery list is the dictionary of the scripts self discoveries
discovery_list = {}
# main_list is the simple list of the scripts discovered and correctly parsed (JSONs)
main_list = []
for s in find_scripts():
    j = discover_script(s)
    if j != None:
        discovery_list[get_description(j)] = j
        main_list.append(get_description(j))

#### main GUI stuff ####
# read configuration, specially agent list
configuration = discover_script(
    f"{os.path.dirname(os.path.realpath(__file__))}/configuration.json")
if configuration == None:
    print("Could not read configuration file... Exiting")
    sys.exit(1)

# due to the time consuming, following part is commented (more in documentation)
# # test which agents are alive
# active_agents = []
# for agent in configuration["agent_list"]:
#     try:
#         master.send_message((agent[0], agent[1]), {"command": "ping"})
#     except:
#         continue
#     active_agents.append((agent[0], agent[1]))
# configuration["agent_list"] = active_agents

root = tk.Tk()
root.tk.call('source', os.path.dirname(
    __file__) + '/Azure-ttk-theme/azure.tcl')
root.tk.call("set_theme", "dark")
root.eval('tk::PlaceWindow . center')
root.title(u"SlowDoS Generator")
# icon loader
text_font_icon = f"{os.path.dirname(os.path.realpath(__file__))}/img/icons8-info-24.png"
_photo = tk.PhotoImage(file=text_font_icon)

# menu part
mainMenu = Menu(root)

menuFile = Menu(mainMenu, tearoff=0)
menuExit = Menu(mainMenu, tearoff=0)
menuTheme = Menu(mainMenu, tearoff=0)


menuFile.add_command(label="Import", command=import_values)
menuFile.add_command(label="Export", command=export_values)
menuExit.add_command(label="Quit", command=root.quit)
mainMenu.add_cascade(label="File", menu=menuFile)
mainMenu.add_cascade(label="Theme", menu=menuTheme)
menuTheme.add_command(label="Change", command=change_theme)
mainMenu.add_cascade(label="Exit", menu=menuExit)

root.config(menu=mainMenu)

# selector frame
#cmb_frame = ttk.Frame(root, style='Card.TFrame', padding=(5, 6, 7, 8))
cmb_frame = LabelFrame(root, text="Choose scripts",
                       font="30", padx=15, pady=15, width=500, height=390)
cmb_frame.grid_propagate(False)

cmb_frame.grid_rowconfigure((0, 2), weight=1)
cmb_frame.grid_columnconfigure(0, weight=1)
cmb_frame.grid(row=1, column=0)
#cmb_frame.place(x=10, y=10, width=400, height=400)


# selector combo
main_combo_selected = tk.StringVar
main_combo = ttk.Combobox(cmb_frame, textvariable=main_combo_selected)
main_combo['state'] = 'readonly'
main_combo['values'] = main_list
main_combo.bind("<<ComboboxSelected>>", lambda _: populate_frame(
    discovery_list[main_combo.get()], main_frame))

main_combo.grid(row=1, column=0)


detail_desc = tk.Message(
    cmb_frame, text="To start choose script")
detail_desc.grid(
    row=2, column=0, padx=10, pady=10, sticky="wn")


# frame
main_frame = LabelFrame(root, text="SlowDosGen", font="30",
                        padx=15, pady=15, width=500, height=510)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid(row=2, column=0)
main_frame.grid_propagate(False)


# agent frame
agents_frame = LabelFrame(root, text="Bots list:",
                          font="30", padx=15, pady=15, width=500, height=390)
agents_frame.grid_propagate(False)


agents_frame.grid_rowconfigure(1, weight=1)
agents_frame.grid_columnconfigure(1, weight=1)
agents_frame.grid(row=1, column=1, padx=10, pady=10)
ttk.Label(agents_frame).grid(
    row=0, column=0, padx=10, pady=10, sticky="wn")
cmb_agents = ttk.Combobox(agents_frame, state="readonly",
                          values=configuration["agent_list"])
cmb_agents.grid(row=1, column=0)
cmb_agents.current(0)
bots_to_run = ttk.Label(
    agents_frame, text="How many bots to run:", image=_photo, compound=tk.RIGHT)
bots_to_run.image = _photo
bots_to_run.grid(
    row=2, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    bots_to_run, text="How many bots out of total number discovered are required to run (number)")


all_agents = IntVar()
all_agents.set(1)
ttk.Entry(agents_frame, textvariable=all_agents).grid(
    row=2, column=1, padx=10, pady=10, sticky="wn")

stat_interval = IntVar()
stat_interval.set(1)
statistic = ttk.Label(agents_frame, text="Statistic interval [seconds]:",
                      image=_photo, compound=tk.RIGHT)
statistic.image = _photo
statistic.grid(row=3, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(statistic, text="How often statistic are taken")
ttk.Entry(agents_frame, textvariable=stat_interval,state="readonly").grid(
    row=3, column=1, padx=10, pady=10, sticky="wn")

warming_up_interval = IntVar()
warming_up_interval.set(1)
agent = ttk.Label(agents_frame, text="Agent start interval [seconds]:",
                  image=_photo, compound=tk.RIGHT)
button1_ttp = CreateToolTip(
    agent, text="Interval after which all agents will be started")
agent.image = _photo
agent.grid(row=4, column=0, padx=10, pady=10, sticky="wn")
ttk.Entry(agents_frame, textvariable=warming_up_interval).grid(
    row=4, column=1, padx=10, pady=10, sticky="wn")

probe_url = StringVar()
probe = ttk.Label(agents_frame, text="Probe URL:",
                  image=_photo, compound=tk.RIGHT)
button1_ttp = CreateToolTip(
    probe, text="URL of the target")
probe.image = _photo
probe.grid(row=5, column=0, padx=10, pady=10, sticky="wn")
ttk.Entry(agents_frame, textvariable=probe_url).grid(
    row=5, column=1, padx=10, pady=10, sticky="wn")

submit_run = ttk.Button(agents_frame, text="Run the script",
                        command=lambda: run_the_script(varList, s, submit_run, ))
submit_run.grid(row=6, column=0)
submit_run.grid_rowconfigure(6, weight=1)
submit_run.grid_columnconfigure(1, weight=1)

cancel_run = ttk.Button(agents_frame, state="disabled", text="Interrupt the script",
                        command=lambda: interrupt_the_script())
cancel_run.grid(row=6, column=1)
cancel_run.grid_rowconfigure(6, weight=1)
cancel_run.grid_columnconfigure(1, weight=1)

# stats frame
stats_frame = LabelFrame(root, text="Runtime statistics",
                         font="30", padx=15, pady=15, width=500, height=510)
stats_frame.grid_propagate(False)

stats_frame.grid_rowconfigure(0, weight=1)
stats_frame.grid_columnconfigure(0, weight=1)
stats_frame.grid(row=2, column=1)

# stats fields
a = ttk.Label(stats_frame).grid(
    row=0, column=0, pady=10, padx=10, sticky="wn")

probe_response = ttk.Label(
    stats_frame, text="Probe response [seconds]", image=_photo, compound=tk.RIGHT)
probe_response.grid(row=1, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    probe_response, text="Current probe response time in seconds")
probe_response.image = _photo

probe_entry = ttk.Label(stats_frame, state="readonly")
probe_entry.grid(
    row=1, column=1, padx=10, pady=10, sticky="wn")

total_agents = ttk.Label(
    stats_frame, text="Number of bots running", image=_photo, compound=tk.RIGHT)
total_agents.grid(row=2, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    total_agents, text="Number of bots currently running")
total_agents.image = _photo

agentcount_entry = ttk.Label(stats_frame, state="readonly")
agentcount_entry.grid(
    row=2, column=1, padx=10, pady=10, sticky="wn")

cpu = ttk.Label(stats_frame, text="CPU (avg %)",
                image=_photo, compound=tk.RIGHT)
cpu.grid(row=3, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(cpu, text="Average cpu usage of all agents")
cpu.image = _photo

cpu_entry = ttk.Label(stats_frame, state="readonly",)
cpu_entry.grid(
    row=3, column=1, padx=10, pady=10, sticky="wn")

memory = ttk.Label(stats_frame, text="Memory (avg %)",
                   image=_photo, compound=tk.RIGHT)
memory.grid(row=4, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(memory, text="Average memory usage of all agents")
memory.image = _photo

mem_entry = ttk.Label(stats_frame, state="readonly")
mem_entry.grid(row=4, column=1, padx=10, pady=10, sticky="wn")

established_connection = ttk.Label(
    stats_frame, text="Established connections (sum)", image=_photo, compound=tk.RIGHT)
established_connection.grid(row=5, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    established_connection, text="Number of established connections with target")
established_connection.image = _photo

established_entry = ttk.Label(stats_frame, state="readonly")
established_entry.grid(
    row=5, column=1, padx=10, pady=10, sticky="wn")

sync = ttk.Label(stats_frame, text="Sync sent (sum)",
                 image=_photo, compound=tk.RIGHT)
sync.grid(row=6, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(sync, text="Number of sync sent to the target")
sync.image = _photo

syncsent_entry = ttk.Label(stats_frame, state="readonly")
syncsent_entry.grid(row=6, column=1, padx=10, pady=10, sticky="wn")

packets_sent = ttk.Label(
    stats_frame, text="Packets sent (sum)", image=_photo, compound=tk.RIGHT)
packets_sent.grid(row=7, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    packets_sent, text="Number of packets sent to the target")
packets_sent.image = _photo


packetsent_entry = ttk.Label(stats_frame, state="readonly")
packetsent_entry.grid(row=7, column=1, padx=10, pady=10, sticky="wn")


packets_rcvd = ttk.Label(
    stats_frame, text="Packets received (sum)", image=_photo, compound=tk.RIGHT)
packets_rcvd.grid(row=8, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    packets_rcvd, text="Number of packets received from the target")
packets_rcvd.image = _photo


packetrcv_entry = ttk.Label(stats_frame, state="readonly")
packetrcv_entry.grid(
    row=8, column=1, padx=10, pady=10, sticky="wn")

bytes_sent = ttk.Label(stats_frame, text="Bytes sent (sum)",
                       image=_photo, compound=tk.RIGHT)
bytes_sent.grid(row=9, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    bytes_sent, text="Number of bytes sent to the target")
bytes_sent.image = _photo


bytesent_entry = ttk.Label(stats_frame, state="readonly")
bytesent_entry.grid(
    row=9, column=1, padx=10, pady=10, sticky="wn")

bytes_rcvd = ttk.Label(
    stats_frame, text="Bytes received (sum)", image=_photo, compound=tk.RIGHT)
bytes_rcvd.grid(row=10, column=0, padx=10, pady=10, sticky="wn")
button1_ttp = CreateToolTip(
    bytes_rcvd, text="Number of received from the target")
bytes_rcvd.image = _photo

bytercv_entry = ttk.Label(stats_frame, state="readonly")
bytercv_entry.grid(
    row=10, column=1, padx=10, pady=10, sticky="wn")

agentstatus_entry = ttk.Label(agents_frame)
agentstatus_entry.grid(
    row=10, column=0, columnspan=2)

if len(discovery_list) == 0:
    print("Could not find anything to run... Exiting")
    sys.exit(1)

main_combo.current(0)
populate_frame(discovery_list[main_list[0]], main_frame)
main_frame.update()
print(main_frame.winfo_width())
print(main_frame.winfo_height())

root.mainloop()

# cleanup - send paranoic DONE messages in try to be sure
try:
    result_queue.put("DONE", block=True, timeout=5)
    status_queue.put("DONE", block=True, timeout=5)
except:
    pass
