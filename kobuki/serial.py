from kobuki.parser import find_packet
from serial import Serial
from parsy import ParseError
from kobuki.commands import serialize
    


class KobukiSerial:

    def __init__(self, port):
        self.remaining = bytes()
        self.port = port

    def send_command(self, cmd):
        self.port.write(serialize(cmd))

    def get_packet(self):
        # Read data in
        # Attempt to parse, if we appear to run out of message, read more and try again
        self.port.timeout = 1
        tries = 0
        data = self.remaining
        while True:
            if (self.port.in_waiting > 0):
                data += self.port.read(self.port.in_waiting)
                try:
                    if len(data) > 0:
                        payloads, remaining = find_packet.parse_partial(data)
                        self.remaining = remaining
                        return payloads
                except ParseError as err:
                    # looking for more bytes
                    if (err.index == len(err.stream)):
                        tries = tries + 1
                        if (tries > 5):
                            tries = 0
                            data = bytes()
                    else:
                        self.port.reset_input_buffer()
                        # some other parse error, clear and try again
                        data = bytes()
