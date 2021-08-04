from struct import unpack_from, calcsize
from parsy import generate, any_char, peek, string, seq, fail
from functools import reduce

from kobuki.data import BasicSensorData, DockingIr, Orientation

@generate
def byte():
    return (yield any_char.map(lambda c: c[0]))


@generate
def le_uint16():
    return (yield byte.times(2).map(lambda bs: int.from_bytes(bs, "little", signed=False)))


@generate
def le_uint32():
    return (yield byte.times(4).map(lambda bs: int.from_bytes(bs, "little", signed=False)))



@generate
def marker():
    return (yield string(bytes([0xAA, 0x55])))

@generate
def header():
    yield marker
    length = yield byte
    return length

@generate
def basic_sensor_data():
    header = yield string(bytes([0x01, 0x0F]))
    basic = seq(
        timestamp = le_uint16,
        bumper = byte,
        wheel_drop = byte,
        cliff = byte,
        left_encoder = le_uint16,
        right_encoder = le_uint16,
        left_pwm = byte,
        right_pwm = byte,
        button = byte,
        charger = byte,
        battery = byte,
        overcurrent = byte
    ).combine_dict(BasicSensorData)

    return (yield basic)

@generate
def docking_ir():
    header = yield string(bytes([0x03, 0x03]))
    right = yield byte
    central = yield byte
    left = yield byte

    return DockingIr(right=right, central=central, left=left)

@generate
def inertial_sensor_data():
    header = yield string(bytes([0x04, 0x07]))
    angle = yield le_uint16
    angle_rate = yield le_uint16
    _ = yield byte.times(3)

    return Orientation(angle, angle_rate)

@generate
def cliff_sensor_data():
    header = yield string(bytes([0x05, 0x06]))
    right = yield le_uint16
    central = yield le_uint16
    left = yield le_uint16

    return right, central, left

@generate
def current():
    header = yield string(bytes([0x06, 0x02]))
    left = yield le_uint16
    right = yield le_uint16

    return left, right

@generate
def raw_gyro():
    header = yield string(bytes([0x0D]))
    length = yield byte
    frame_id = yield byte
    data_length = (yield byte) / 3

    gyro_data = (le_uint16.times(3)).times(data_length)

    return gyro_data

@generate
def gpio():
    header = yield string(bytes([0x10, 0x10]))
    digital_input = yield le_uint16
    analog_input0 = yield le_uint16
    analog_input1 = yield le_uint16
    analog_input2 = yield le_uint16
    analog_input3 = yield le_uint16
    _ = yield le_uint16.times(3)

    return digital_input, analog_input0, analog_input1, analog_input2, analog_input3


@generate
def subpayload():
    payload = yield basic_sensor_data.tag('basic') | \
                    docking_ir.tag('docking_ir') | \
                    inertial_sensor_data.tag('inertial') | \
                    cliff_sensor_data.tag('cliff') | \
                    current.tag('current') | \
                    raw_gyro.tag('gyro') | \
                    gpio.tag('gpio')

    return payload

@generate
def all_subpayloads():
    ps = dict()
    p = yield subpayload.optional()
    while p is not None:
        k, v = p
        ps[k] = v
        p = yield subpayload.optional()
    return ps

@generate
def packet():
    packet_length = yield header
    all_bytes = yield byte.times(packet_length)
    checksum = yield byte

    valid = (checksum == reduce(lambda s, b: s ^ b, all_bytes, 0))

    return all_bytes, valid

@generate
def find_packet():
    raw_bytes, valid = yield (header.should_fail('no header') >> any_char).many() >> packet
    payloads, _ = all_subpayloads.parse_partial(bytes(raw_bytes))
    return payloads


