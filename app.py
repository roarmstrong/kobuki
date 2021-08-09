from kobuki.kobuki import Kobuki
from serial import Serial
from kobuki.commands import BaseControl
from kobuki.data.basicsensordata import ChargerState
from time import monotonic, sleep
import math

def main():

    move_forward = BaseControl(50, 0)
    move_backward = BaseControl(-50, 0)
    stop = BaseControl(0, 0)
    spin_cw = BaseControl(50, -1)
    spin_ccw = BaseControl(50, 1)

    with Serial("/dev/ttyUSB0", 115200) as port:
        kobuki = Kobuki(port)
        while True:
            print(f"x: {kobuki.state.x:.10f}m y: {kobuki.state.y:.10f}m θ: {kobuki.state.theta:.10f}rad")
            if kobuki.state.bumper_activated:
                kobuki.send_command(stop)
                sleep(0.5)
            else:
                sleep(0.5)
                # do something else! e.g.
                # kobuki.send_command(spin_ccw)
                # kobuki.send_command(move_forward)




if __name__ == "__main__":
    main()
