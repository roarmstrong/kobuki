import struct
from operator import xor
from functools import reduce


def serialize(cmd):
    return cmd.serialize()

class Command:
    def serialize(self, payload):
        header = bytes([0xAA, 0x55, len(payload)])
        checksum = bytes([reduce(xor, payload)])
        return header + payload + checksum


class BaseControl(Command):

    def __init__(self, speed, radius):
        self.id = 0x01
        self.length = 0x04
        self.speed = speed
        self.radius = radius

    def serialize(self):
        return super().serialize(struct.pack("<BBhh", self.id, self.length, self.speed, self.radius))


class BaseControlSi(Command):

    def __init__(self, speed, radius):
        pass

    def serialize(self):
        pass

