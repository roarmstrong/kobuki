class IrData:
    def __init__(self, near_left, near_center, near_right, far_center, far_left, far_right):
        self.near_left = near_left
        self.near_center = near_center
        self.near_right = near_right
        self.far_center = far_center
        self.far_left = far_left
        self.far_right = far_right

    def __str__(self):
        return "nl: "    + str(self.near_left) + " " + \
                "nc: " + str(self.near_center) + " " + \
                "nr: "  + str(self.near_right) + " " + \
                "fl: "    + str(self.far_left) + " " + \
                "fc: "  + str(self.far_center) + " " + \
                "fr: "   + str(self.far_right)


def _flags(data):
    NEAR_LEFT = 0x01
    NEAR_CENTER = 0x02
    NEAR_RIGHT = 0x04
    FAR_CENTER = 0x08
    FAR_LEFT = 0x10
    FAR_RIGHT = 0x20

    return IrData(
        near_left = (data & NEAR_LEFT) != 0,
        near_center = (data & NEAR_CENTER) != 0,
        near_right = (data & NEAR_RIGHT) != 0,
        far_center = (data & FAR_CENTER) != 0,
        far_left = (data & FAR_LEFT) != 0,
        far_right = (data & FAR_RIGHT) != 0
    )


class DockingIr:

    def __init__(self,
        left,
        central,
        right
    ):
        self.raw_left = left
        self.raw_central = central
        self.raw_right = right
        self.left = _flags(left)
        self.right = _flags(right)
        self.central = _flags(central)