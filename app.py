from kobuki.serial import KobukiSerial
from serial import Serial
from kobuki.commands import BaseControl
from kobuki.data.basicsensordata import ChargerState
from kobuki.state import KobukiState
from time import monotonic
import math

def main():

    move_forward = BaseControl(50, 0)
    move_backward = BaseControl(-50, 0)
    stop = BaseControl(0, 0)
    spin_cw = BaseControl(50, -1)
    spin_ccw = BaseControl(50, 1)

    with Serial("/dev/ttyUSB0", 115200) as port:
        kobuki = KobukiSerial(port)
        kobuki_state = KobukiState()
        x = kobuki_state.x
        y = kobuki_state.y
        should_turn = False
        while True:
            data = kobuki.get_packet()
            ir = data['docking_ir']
            basic = data['basic']
            inertial = data['inertial']
            kobuki_state.updateBasicSensorData(basic)
            kobuki_state.updateOrientation(inertial)


            if kobuki_state.bumper_activated:
                kobuki.send_command(stop)
            else:
                distance = math.sqrt(((x - kobuki_state.x) ** 2) + ((y - kobuki_state.y) ** 2))
                kobuki.send_command(move_backward)
                if distance > 0.1:
                    print(distance)
                    should_turn = True
                if should_turn:
                    kobuki.send_command(spin_ccw)
                    should_turn = False
                    x = kobuki_state.x
                    y = kobuki_state.y
                # do something else!
                # e.g. kobuki.send_command(spin_ccw)
                # kobuki.send_command(move_forward)




if __name__ == "__main__":
    main()
