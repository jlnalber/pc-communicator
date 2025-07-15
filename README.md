# LEGO PC Communicator

## What it does?

The PC Communicator is a python script that can communicate with multiple [LEGO Technic Hubs](https://www.lego.com/de-de/product/technic-hub-88012). It consists of a script for the computer, a script for the main hub, and a script for the butler hub.
The computer sends commands via a user interface to a main hub, which then redirects these commands to the other hubs (butler hubs).

## How to set it up?

Via [Pybricks Code](https://code.pybricks.com/), install MicroPython on all your Technic Hubs. It is indispensable that the main hub is named "Batteriebox 1".
Upload the python script for the main hub to the main hub and respectively for the butler hubs. This procedure only has to be followed once. Thereafter, you can start with the following steps immediately.

Now, shut off all of the hubs. Restart the main hub by pressing on its power button once. The light should blink blue.
Then, run the [main.py](/main.py) script on your computer (some libraries possibly still need to be installed as well as python itself). It will then automatically connect with the hub. If you encounter any issues, try turning the hub off and on again. During testing, I often had connectivity issues whose only solution was patience.
If everything went accordingly, you will now be prompted to start the program on the main hub by pushing the button. Thereafter, a window will open.
