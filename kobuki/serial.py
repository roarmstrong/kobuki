from kobuki.parser import find_packet
from serial import Serial
from serial.threaded import ReaderThread, Protocol
from threading import Thread, Lock
from parsy import ParseError
from kobuki.commands import serialize


class KobukiSerialProtocol(Protocol):

    def __init__(self, lock):
        self.lock = lock

    def connection_made(self, transport):
        pass

    def data_received(self, data):
        pass

    def connection_lost(self, exc):
        pass


class ThreadedKobukiSerial:

    def start(self):
        self.lock = Lock()
        self.port = Serial("/dev/ttyUSB0", 115200)
        self.reader_thread = ReaderThread(self.port, lambda: KobukiSerialProtocol(self.lock) )
        transport, protocol = self.reader_thread.connect()

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
        print(data)
        while True:
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
        