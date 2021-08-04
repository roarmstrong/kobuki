from kobuki.serial import KobukiSerial
from serial import Serial
from kobuki.commands import BaseControl
from kobuki.data.basicsensordata import ChargerState
from time import monotonic

def onCenter(ir):
    return ir.central.near_center or ir.central.far_center

def onLeft(ir):
    return ir.central.near_left or ir.central.far_left

def onRight(ir):
    return ir.central.near_right or ir.central.far_right

def docked(data):
    return (data.charger == ChargerState.DOCKING_CHARGING) or (data.charger == ChargerState.DOCKING_CHARGED)

def bumperActivated(data):
    return data.bumper['central'] or data.bumper['left'] or data.bumper['right']

def main():
    go = BaseControl(60, 0)
    stop = BaseControl(0, 0)
    spin_ccw = BaseControl(50, 1)
    spin_cw = BaseControl(-50, 1)

    with Serial("/dev/ttyUSB0", 115200) as port:
        kobuki = KobukiSerial(port)
        lastSeen = monotonic()
        seen = False
        while True:
            now = monotonic()
            data = kobuki.get_packet()
            print('got packet?')
            ir = data['docking_ir']
            basic = data['basic']
            if docked(basic) or bumperActivated(basic):
                kobuki.send_command(stop)
            elif onCenter(ir) and not onLeft(ir) and onRight(ir):
                seen = True
                lastSeen = now
                print("inbound!")
                kobuki.send_command(go)
            elif onCenter(ir) and onLeft(ir):
                print("going left!")
                kobuki.send_command(go)
            elif onCenter(ir) and onRight(ir):
                print("going right")
                kobuki.send_command(go)
            elif not seen and now - lastSeen > 2:
                print("spinning")
                kobuki.send_command(spin_cw)


if __name__ == "__main__":
    main()
