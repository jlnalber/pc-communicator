# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Henrik Blidh
# Copyright (c) 2022-2023 The Pybricks Authors

"""
Example program for computer-to-hub communication.

Requires Pybricks firmware >= 3.3.0.
"""

import sys
sys.coinit_flags = 0 


import asyncio
import tk_async_execute as tae
from contextlib import suppress
from bleak import BleakScanner, BleakClient

import json

from tkinter import *
from tkinter import ttk
import tkinter.messagebox

import time

import asyncio
import tkinter as tk
from tkinter import messagebox

import threading

import json

keybindings = None
try:
    with open("keybindings.json") as f:
        keybindings = json.load(f)
except:
    pass
print(keybindings)



try:
    from bleak.backends.winrt.util import allow_sta
    # tell Bleak we are using a graphical user interface that has been properly
    # configured to work with asyncio
    allow_sta()
except ImportError:
    # other OSes and older versions of Bleak will raise ImportError which we
    # can safely ignore
    pass

listOfHubs = []
hubsVars = []

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware.
HUB_NAME = "Batteriebox 1"


# initialize the root window
root = None


async def main():

    main_task = asyncio.current_task()

    def handle_disconnect(_):

        tkinter.messagebox.showerror("Verbindung getrennt", "Die Verbindung zum Hub wurde getrennt.")
        print("Hub was disconnected.")

        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        if not main_task.done():
            main_task.cancel()

    ready_event = asyncio.Event()

    def createCheckboxForHub():
        if root is not None:
            hubsVars.append(IntVar())
            cbox = Checkbutton(root, text="Hub " + str(len(hubsVars) - 1), variable=hubsVars[-1], onvalue=1, offvalue=0)
            cbox.grid(column=0, row=len(hubsVars) - 1)
            print("Added checkbox for hub", str(len(hubsVars) - 1))


    def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]

            if payload == b"rdy":
                ready_event.set()
            else:
                s = payload.split(b":")
                print("Received:", payload)
                if len(s) == 2 and s[0] == b"reportHub":
                    print (s[1])
                    if not s[1] in listOfHubs:
                        listOfHubs.append(s[1])
                        if not s[1] == b"0":
                            # Create a new checkbox for the hub
                            # this usually never works
                            createCheckboxForHub()
            
            

    # Do a Bluetooth scan to find the hub.
    device = await BleakScanner.find_device_by_name(HUB_NAME)

    # connect to device
    while device is None:
    
        response = tkinter.messagebox.askretrycancel(title="404", message="Hub mit dem Namen '" + HUB_NAME + "' nicht gefunden.")
        print(f"could not find hub with name: {HUB_NAME}")
        print(response)
        if not response:
            return

        device = await BleakScanner.find_device_by_name(HUB_NAME)

    print(f"Found hub with name: {HUB_NAME}")
        
    # Connect to the hub.
    async with BleakClient(device, handle_disconnect) as client:

        # Subscribe to notifications from the hub.
        print("Subscribing to notifications from the hub...")
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
        print("Subscribed to notifications from the hub.")

        # Shorthand for sending some data to the hub.
        async def send(data, re):
            # Wait for hub to say that it is ready to receive data.
            try:
                # loop = asyncio.get_running_loop()
                try:
                    await re.wait()
                except Exception as e:
                    # it probably crashes here because the event is
                    pass
                
                print("received ready")
                # Prepare for the next ready event.
                re.clear()
            except:
                print("blubberlutsch")
            # Send the data to the hub.
            await client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data,  # prepend "write stdin" command (0x06)
                response=True
            )

        async def sendMultiple(datas, re):
            for data in datas:
                await send(data, re)

        async def connectFillAndSendMultiple(ds, re):
            await sendMultiple([connectAndFill(d) for d in ds], re)

        # Tell user to start program on the hub.
        tkinter.messagebox.showinfo("Programm starten", "Programm jetzt mit dem Button starten!")
        print("Start the program on the hub now with the button.")

        # Send a few messages to the hub.
        await send(b"reportHub?", ready_event)


        def run_async_task(event_loop, params, ready_event):
            asyncio.set_event_loop(event_loop)
            event_loop.run_until_complete(connectFillAndSendMultiple(params, ready_event))

        def start_async_task(params, ready_event):
            # Erstellen Sie eine neue Ereignisschleife für den Thread
            new_loop = asyncio.new_event_loop()
            # Starten Sie die asynchrone Aufgabe in einem separaten Thread
            threading.Thread(target=run_async_task, args=(new_loop, params, ready_event)).start()

        
        def onKeyPress(event):
            try:
                commands = keybindings[event.char]
                start_async_task(commands, ready_event)
            except:
                pass


        root = tk.Tk()
        root.title("Lego Controller")

        # add checkboxes for ports
        ports = [IntVar(), IntVar(), IntVar(), IntVar()]
        cboxPortA = Checkbutton(root, text="Port A", variable=ports[0], onvalue=1, offvalue=0)
        cboxPortA.grid(column=1, row=0)
        cboxPortB = Checkbutton(root, text="Port B", variable=ports[1], onvalue=1, offvalue=0)
        cboxPortB.grid(column=1, row=1)
        cboxPortC = Checkbutton(root, text="Port C", variable=ports[2], onvalue=1, offvalue=0)
        cboxPortC.grid(column=1, row=2)
        cboxPortD = Checkbutton(root, text="Port D", variable=ports[3], onvalue=1, offvalue=0)
        cboxPortD.grid(column=1, row=3)

        # add checkboxes for hubs
        hubsVars = [IntVar()]
        cboxHub0 = Checkbutton(root, text="Hub 0", variable=hubsVars[0], onvalue=1, offvalue=0)
        cboxHub0.grid(column=0, row=0)

        # add a slider for speed
        try:
            slider = Scale(root, from_=-100, to=100, orient=HORIZONTAL, label="Geschwindigkeit")
            slider.grid(column=2)
        except:
            pass

        # The Buttons to start and stop the program.
        btnStart = Button(root, text="Sende", command=lambda:
            start_async_task(generateCommandsFromHubsAndPortsVars(hubsVars, ports, round(slider.get())), ready_event))#, column=0, row=2)
        btnStart.grid(sticky="SW", column=2)
        btnStop = Button(root, text="Stop", command=lambda:
            start_async_task(generateCommandsFromHubsAndPortsVars(hubsVars, ports, "stop"), ready_event))#, column=1, row=2)
        btnStop.grid(sticky="SW", column=2)
        btnAddHub = Button(root, text="Füge Hub hinzu", command=createCheckboxForHub)#, column=2, row=2)
        btnAddHub.grid(sticky="SW", column=2)
        btnConnect = Button(root, text="Verbinde mit anderen Hubs", command=lambda:
            start_async_task([["connect"]], ready_event))#, column=2, row=2)
        btnConnect.grid(sticky="SW", column=2)

        # add keybindings
        root.bind('<KeyPress>', onKeyPress)
        root.mainloop()

        await send(b"bye=======", ready_event)

        # remove comment to enable command line mode run in loop
        # await runinloop(send, ready_event)


        # Send a message to indicate stop.
        print("done.")

    # Hub disconnects here when async with block exits.

def connectAndFill(params):
    res = ""
    for i in params:
        res += i + ":"
    res = res[:-1]  # Remove trailing colon
    while len(res) < 10:
        res += "="
    return res.encode('utf-8')

def generateCommandsFromHubsAndPorts(hubs, ports, speed):
    res = []
    for hub in hubs:
        for port in ports:
            res.append([hub, port, str(speed)])
    return res

def generateCommandsFromHubsAndPortsVars(hubsVars, portsVars, speed):
    hubs = []
    for i in range(len(hubsVars)):
        if hubsVars[i].get() == 1:
            hubs.append(str(i))
    ports = []
    portsAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(len(portsVars)):
        if portsVars[i].get() == 1:
            ports.append(portsAlphabet[i])
    return generateCommandsFromHubsAndPorts(hubs, ports, speed)

async def runinloop(send, ready_event):
    activeHub = None
    activePort = None
    while True:
        text = input("Warte auf Eingabe: ")
        parts = text.split(" ")

        def checkParts(hub, port):
            if hub is None or port is None:
                print("Bitte Hub und Port angeben!")
                return False
            return True

        if len(parts) >= 2:
            if (parts[0] == "hub"):
                activeHub = parts[1]
                activePort = None
            elif (parts[0] == "port"):
                activePort = parts[1]
            elif (parts[0] == "run"):
                print(connectAndFill([activeHub, activePort, *parts[1:]]))
                if not checkParts(activeHub, activePort):
                    continue
                await send(connectAndFill([activeHub, activePort, *parts[1:]]), ready_event)


        elif text == "stop":
            if not checkParts(activeHub, activePort):
                continue
            await send(connectAndFill([activeHub, activePort, "stop"]), ready_event)
        
        elif text == "connect":
            await send(connectAndFill(["connect"]), ready_event)

        elif text == "exit":
            break
        
        
# Run the main async program.
if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        try:
            asyncio.run(main())
        except OSError:
            tkinter.messagebox.showerror("Fehler aufgetreten", "Bluetooth bitte anschalten.")

# protocol
# 
# reportHub:{ID}
# reportMotor:{HUBID}:{PORT}

# hub: rdy
# computer: reportHub?
# hub: reportHub:{ID}
# computer: reportSensorsOnHub:{HUBID}