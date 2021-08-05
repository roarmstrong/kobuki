import struct
from operator import xor
from functools import reduce

# function to call serialize on a Command object
def serialize(cmd):
    return cmd.serialize()

# Base class for Kobuki commands
# Derived classes should call this serialize() method
# to create bytes for Kobuki
class Command:
    def serialize(self, payload):
        header = bytes([0xAA, 0x55, len(payload)])
        checksum = bytes([reduce(xor, payload)])
        return header + payload + checksum

# BaseControl provides movement commands for Kobuki
# speed is expressed in mm / s
# +ve speed is forward motion, -ve speed is reverse motion
# radius is expressed in mm
# +ve radius will move robot in ccw arc, -ve radius will move robot in cw arc
# radius of 0 == pure translation
# radius of 1 == pure rotation
class BaseControl(Command):

    def __init__(self, speed, radius):
        self.id = 0x01
        self.length = 0x04
        self.speed = speed
        self.radius = radius

    def serialize(self):
        return super().serialize(struct.pack("<BBhh", self.id, self.length, self.speed, self.radius))

