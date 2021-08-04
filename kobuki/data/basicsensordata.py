from enum import Enum

def _bumper_flags(data):
    RIGHT = 0x01
    CENTRAL = 0x02
    LEFT = 0x04

    return {
        "right": (data & RIGHT) != 0,
        "central": (data & CENTRAL) != 0,
        "left": (data & LEFT) != 0
    }

def _wheel_drop_flags(data):
    RIGHT = 0x01
    LEFT = 0x02

    return {
        "right": (data & RIGHT) != 0,
        "left": (data & LEFT) != 0
    }

def _cliff_flags(data):
    RIGHT = 0x01
    CENTRAL = 0x02
    LEFT = 0x04

    return {
        "right": (data & RIGHT) != 0,
        "central": (data & CENTRAL) != 0,
        "left": (data & LEFT) != 0
    }


class ChargerState(Enum):
    DISCHARGING = 0
    DOCKING_CHARGED = 2
    DOCKING_CHARGING = 6
    ADAPTER_CHARGED = 18
    ADAPTER_CHARGING = 22


def _charger_flags(data):
    return ChargerState(data)


# https://yujinrobot.github.io/kobuki/enAppendixKobukiParameters.html
def encoder_to_metres(data):
    return data

def encoder_to_radians(data):
    return data

class BasicSensorData:

    def __init__(self,
        timestamp,
        bumper,
        wheel_drop,
        cliff,
        left_encoder,
        right_encoder,
        left_pwm,
        right_pwm,
        button,
        charger,
        battery,
        overcurrent,
    ):
        self.timestamp = timestamp
        self.bumper = _bumper_flags(bumper)
        self.wheel_drop = _wheel_drop_flags(wheel_drop),
        self.cliff = _cliff_flags(cliff)
        self.left_encoder = left_encoder
        self.right_encoder = right_encoder
        self.left_pwm = left_pwm
        self.right_pwm = right_pwm
        self.button = button
        self.charger = _charger_flags(charger)
        self.battery = battery
        self.overcurrent = overcurrent

    def __str__(self):
        return str(self.timestamp) + ", " + \
               str(self.bumper) + ", " + \
               str(self.left_encoder) + ", " + \
               str(self.right_encoder)