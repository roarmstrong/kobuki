from kobuki.serial import KobukiSerial
from serial import Serial
from kobuki.commands import BaseControl
from kobuki.data.basicsensordata import ChargerState
from time import monotonic

def main():

    with Serial("/dev/ttyUSB0", 115200) as port:
        kobuki = KobukiSerial(port)
        while True:
            data = kobuki.get_packet()
            ir = data['docking_ir']
            basic = data['basic']
            print("Basic Data: ", basic)
            print("Docking IR: ", ir)


if __name__ == "__main__":
    main()
