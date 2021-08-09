from kobuki.data import BasicSensorData, DockingIr, Orientation
import math

# contains information about the current Kobuki state
# for example, distance travelled, current angle, bumper activation
class KobukiState:

    def __init__(self):
        self._raw_left = None
        self._raw_right = None
        self._initial_angle = None

        self.bumper_activated = False
        self.angle = 0

        self.x = 0
        self.y = 0
        self.phi = 0


    def updateOrientation(self, orientation):
        if self._initial_angle is None:
            self._initial_angle = orientation.angle

        self.angle = ((2 * math.pi) / 65535) * (orientation.angle - self._initial_angle)
        # print(self.angle)


    def updateBasicSensorData(self, basic):
        if self._raw_left is None:
            self._raw_left = basic.left_encoder
        if self._raw_right is None:
            self._raw_right = basic.right_encoder

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

        # calculate change in meters
        delta_l_metres = delta_l *  0.000085292090497737556558
        delta_r_metres = delta_r *  0.000085292090497737556558

        delta_centre = (delta_l_metres + delta_r_metres) / 2
        orientation = (delta_r_metres - delta_l_metres) / 0.23

        x = delta_centre * math.cos(orientation)
        y = delta_centre * math.sin(orientation)

        self.x = self.x + x
        self.y = self.y + y
        self.phi = self.angle

        self.bumper_activated = basic.bumper['left'] or basic.bumper['right'] or basic.bumper['central']