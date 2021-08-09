from kobuki.parser import find_packet
from serial import Serial
from parsy import ParseError
from kobuki.commands import serialize
from serial.threaded import Protocol, ReaderThread
from enum import Enum

class ReadReturn(Enum):
    OK = 0
    NEED_MORE = 1
    PARSE_ERROR = 2

def _get_packet(data):
    try:
        if len(data) > 0:
            payloads, remaining = find_packet.parse_partial(data)
            return payloads, remaining, ReadReturn.OK
    except ParseError as err:
        # looking for more bytes
        if (err.index == len(err.stream)):
            return dict(), data, ReadReturn.NEED_MORE
        else:
            # couldn't parse packet, clear this set of bytes
            return dict(), bytes(), ReadReturn.PARSE_ERROR

class KobukiProtocol(Protocol):

    def __init__(self, kobuki_state):
        self.writer = None
        self.remaining = bytes()
        self.kobuki_state = kobuki_state

    def connection_made(self, transport):
        self.writer = transport

    def data_received(self, data):
        to_process = self.remaining + data
        payloads, remaining, error = _get_packet(to_process)
        if error == ReadReturn.OK:
            self.remaining = remaining
            self.kobuki_state.updatePayloads(payloads)
        else:
            self.remaining = remaining

    def connection_lost(self, exc):
        self.writer = None

    def write(self, to_write):
        if self.writer is not None:
            self.writer.write(to_write)


class KobukiSerial:

    def __init__(self, port, kobuki_state):
        self.rt = ReaderThread(port, lambda: KobukiProtocol(kobuki_state))
        self.rt.start()
        _, self.protocol = self.rt.connect()


    def send_command(self, cmd):
        self.protocol.write(serialize(cmd))




