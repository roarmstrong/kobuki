from kobuki.data import BasicSensorData, DockingIr, Orientation
import math
from threading import Lock
from numpy import uint16, int16
import warnings

# contains information about the current Kobuki state
# for example, distance travelled, current angle, bumper activation
class KobukiState:

    def __init__(self):
        self._raw_left = None
        self._raw_right = None
        self._initial_angle = None

        self.bumper_activated = False # if any bumpers (right, left, central are active)
        self.angle = 0 # orientation as measured by gyro

        self.x = 0 # cartesian x in m
        self.y = 0 # cartesian y in m
        self.theta = 0 # orientation measured by wheel encoders

        self.lock = Lock() # write lock to prevent multiple updates


    # lock here to prevent multiple updates
    # not threadsafe for reads, but will ignore this
    # for simplicity
    def updatePayloads(self, payloads):
        with self.lock:
            if 'inertial' in payloads:
                self.updateOrientation(payloads['inertial'])
            if 'basic' in payloads:
                self.updateBasicSensorData(payloads['basic'])


    def updateOrientation(self, orientation):
        if self._initial_angle is None:
            self._initial_angle = orientation.angle

        self.angle = ((2 * math.pi) / 65535) * (orientation.angle - self._initial_angle)


    def updateBasicSensorData(self, basic):
        left = uint16(basic.left_encoder)
        right = uint16(basic.right_encoder)
        # if 1st packet, set raw values
        if self._raw_left is None:
            self._raw_left = left
        if self._raw_right is None:
            self._raw_right = right

        # this will account for rollover in the unsigned encoder values
        # up to the range of int16. If the delta is beyond we will not be
        # able to determine the correct delta
        # numpy helpfully warns us about the under/overflow
        # but it is intended, so suppress the warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            delta_l = int(int16(left - self._raw_left))
            delta_r = int(int16(right - self._raw_right))

        self._raw_left = left
        self._raw_right = right

        # calculate left and right wheel deltas in meters
        # values taken from https://yujinrobot.github.io/kobuki/enAppendixProtocolSpecification.html
        delta_l_metres = delta_l *  0.000085292090497737556558
        delta_r_metres = delta_r *  0.000085292090497737556558

        delta_centre = (delta_l_metres + delta_r_metres) / 2
        phi = (delta_r_metres - delta_l_metres) / 0.23 # change in orientation measured by wheel encoders

        x = delta_centre * math.cos(self.angle) # delta x in metres
        y = delta_centre * math.sin(self.angle) # delta y in metres

        self.x = self.x + x
        self.y = self.y + y
        self.theta = (self.theta + phi) % (2 * math.pi)

        self.bumper_activated = basic.bumper['left'] or basic.bumper['right'] or basic.bumper['central']
