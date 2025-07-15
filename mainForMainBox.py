from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Color
from pybricks.tools import wait
from pybricks.hubs import TechnicHub
import ustruct


# Standard MicroPython modules
from usys import stdin, stdout
from uselect import poll

hub = TechnicHub(broadcast_channel=1, observe_channels=[1])

motorA = None
motorB = None
motorC = None
motorD = None

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


hubCount = 0

# Optional: Register stdin for polling. This allows
# you to wait for incoming data without blocking.
keyboard = poll()
keyboard.register(stdin)

lastCmd = None
lastData = None

while True:

    # Let the remote program know we are ready for a command.
    stdout.buffer.write(b"rdy")

    # Optional: Check available input.
    # while not keyboard.poll(0):
        # Optional: Do something here.
        # wait(10)

    # Read three bytes.
    cmd = stdin.buffer.read(10)

    # Mache nur etwas, wenn ein neuer Command angekommen ist
    if (lastCmd != cmd):
        lastCmd = cmd

        # Decide what to do based on the command.
        s = cmd.split(b":")

        try:
            if len(s) == 1:
                if cmd == b"start=====":
                    stdout.buffer.write(b"Hallo Welt")
                    # hub.light.blink(Color.GREEN, [500, 500])
                elif cmd == b"reportHub?":
                    stdout.buffer.write(b"reportHub:0")
                elif cmd == b"bye=======":
                    break
                elif cmd == b"connect===":
                    pass # then, it will continue to the next loop where it will check for another hub
            elif len(s) == 3:
                if s[0] == b"0":
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
                else:
                    # then, we have to broadcast it
                    hub.ble.broadcast(cmd)
        except:
            pass

    data = hub.ble.observe(1)
    if data is not None and data != lastData:
        lastData = data
        split = data.split(":")
        # hub.light.on(Color.WHITE)
        if split[0] == "report":
            # then, there is a new device. Connect!
            config = split[1]
            hubCount += 1
            hub.ble.broadcast(str(config) + ":" + str(hubCount))

            stdout.buffer.write(ustruct.pack("11sB", "reportHub:" + str(hubCount)))
            # hub.light.on(Color.RED)
        


