from pybricks.hubs import TechnicHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from urandom import random
from umath import floor
import ustruct

hub = TechnicHub(broadcast_channel=1, observe_channels=[1])

motorA = None
motorB = None
motorC = None
motorD = None

differenceByteAndNumber = 48

# print(b"5"[0]) # TODO: man muss diesen Wert einfach -48 rechnen
# r = b"basrlkaj:3"
# s = r.split(b":")
# if 3 == (s[1][0] - 48):
#     hub.light.on(Color.ORANGE)
# else:
#     hub.light.on(Color.GREEN)
# wait(5000)

try:
    motorA = Motor(Port.A)
except:
    pass
try:
    motorB = Motor(Port.B)
except:
    pass
try:
    motorC = Motor(Port.C)
except:
    pass
try:
    motorD = Motor(Port.D)
except:
    pass

N = 10
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
config = ''.join(chars[floor(random() * (len(chars)))] for _ in range(N))
num = None

lastData = None

hub.light.on(Color.BLUE)

while True:
    # ask for connection
    data = hub.ble.observe(1)
    if data is not None:
        lastData = data
        split = data.split(":")
        if split[0] == config:


            try:
                num = int(split[1])
            except:
                hub.light.on(Color.RED)
            break
    
    # otherwise, send again
    hub.ble.broadcast("report:" + config)

hub.light.on(Color.GRAY)

def convert(num):
    # for decimals larger or equal to 10
    length = len(num)
    res = 0
    for i in range(length):
        n = num[i] - differenceByteAndNumber
        res = res + n * 10 ** (length - 1 - i)
    return res

while True:
    # listen for a command
    data = hub.ble.observe(1)

    if data is not None and data != lastData:
        
        lastData = data
        try:
            # Decide what to do based on the command.
            s = data.split(b":")

            if len(s) == 3:
                if convert(s[0]) == num:
                    motor = None            
                    if s[1] == b"A":
                        motor = motorA
                    elif s[1] == b"B":
                        motor = motorB
                    elif s[1] == b"C":
                        motor = motorC
                    elif s[1] == b"D":
                        motor = motorD

                    if s[2] == b"stop==":
                        motor.stop()
                    else:
                        d = s[2].split(b"=")[0]
                        motor.dc(int(d))
        except:
            pass
