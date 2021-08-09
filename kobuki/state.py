from kobuki.data import BasicSensorData, DockingIr, Orientation
import math
from threading import Lock

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
        # if 1st packet, set raw values
        if self._raw_left is None:
            self._raw_left = basic.left_encoder
        if self._raw_right is None:
            self._raw_right = basic.right_encoder

        # check for rollover in encoder values
        # to determine delta in left and right encoder values
        if self._raw_left > 65500 and basic.left_encoder < 1000:
            delta_l = (65535 - self._raw_left) + basic.left_encoder
        elif self._raw_left < 1000 and basic.left_encoder > 65500:
            delta_l = (65535 - basic.left_encoder) + self._raw_left
        else:
            delta_l = basic.left_encoder - self._raw_left

        if self._raw_right > 65500 and basic.right_encoder < 1000:
            delta_r = (65535 - self._raw_right) + basic.right_encoder
        elif self._raw_right < 1000 and basic.right_encoder > 65500:
            delta_r = (65535 - basic.right_encoder) + self._raw_right
        else:
            delta_r = basic.right_encoder - self._raw_right

        self._raw_left = basic.left_encoder
        self._raw_right = basic.right_encoder

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
        self.theta = self.theta + phi

        self.bumper_activated = basic.bumper['left'] or basic.bumper['right'] or basic.bumper['central']
