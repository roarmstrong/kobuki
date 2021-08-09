from kobuki.serial import KobukiSerial
from kobuki.state import KobukiState

class Kobuki:

    def __init__(self, port):
        self.state = KobukiState()
        self.comms = KobukiSerial(port, self.state)

    def send_command(self, cmd):
        self.comms.send_command(cmd)

