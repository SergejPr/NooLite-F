from enum import IntEnum
from serial import Serial
from struct import Struct


class Command(IntEnum):
    OFF = 0,
    BRIGHT_DOWN = 1,
    ON = 2,
    BRIGHT_UP = 3,
    SWITCH = 4,
    BRIGHT_BACK = 5,
    SET_BRIGHTNESS = 6,
    LOAD_PRESET = 7,
    SAVE_PRESET = 8,
    UNBIND = 9,
    STOP_BRIGHT = 10,
    BRIGHT_STEP_DOWN = 11,
    BRIGHT_STEP_UP = 12,
    BRIGHT_REG = 13,
    BIND = 15,
    ROLL_COLOR = 16,
    SWITCH_COLOR = 17,
    SWITCH_MODE = 18,
    SPEED_MODE = 19,
    BATTERY_LOW = 20,
    SENS_TEMP_HUMI = 21,
    TEMPORARY_ON = 25,
    MODES = 26,
    READ_STATE = 128,
    WRITE_STATE = 129,
    SEND_STATE = 130,
    SERVICE = 131,
    CLEAR_MEMORY = 132


class Mode(IntEnum):
    TX = 0,
    RX = 1,
    TX_F = 2,
    RX_F = 3,
    SERVICE = 4,
    FIRMWARE_UPDATE = 5


class ResponseCode(IntEnum):
    SUCCESS = 0,
    NO_RESPONSE = 1,
    ERROR = 2,
    BIND_SUCCESS = 3


class Action(IntEnum):
    SEND_COMMAND = 0,
    SEND_BROADCAST_COMMAND = 1,
    READ_RESPONSE = 2,
    BIND_MODE_ON = 3,
    BIND_MODE_OFF = 4,
    CLEAR_CHANNEL = 5,
    CLEAR_MEMORY = 6,
    UNBIND_ADDRESS_FROM_CHANNEL = 7,
    SEND_COMMAND_BY_ADDRESS = 8


class ResponseException(Exception):
    """Base class for response exceptions."""


class Request(object):
    mode: Mode = Mode.TX
    action: Action = Action.SEND_COMMAND
    channel: int = 0
    command: Command = Command.OFF
    format: int = 0
    data: bytearray = bytearray(4)
    id: int = 0

    def __repr__(self):
        return "<Request (0x{0:x}), mode: {1}, action: {2}, channel: {3:d}, command: {4:d}, format: {5:d}, data: {6}, id: 0x{7:x}>"\
            .format(id(self), self.mode, self.action, self.channel, self.command, self.format, self.data, self.id)


class Response(object):
    mode: Mode = None
    status: ResponseCode = None
    channel: int = None
    command: Command = None
    count: int = None
    format: int = None
    data: bytearray = None
    id: int = None

    def __repr__(self):
        return "<Response (0x{0:x}), mode: {1}, status: {2}, channel: {3:d}, command: {4:d}, format: {5:d}, data: {6}, id: 0x{7:x}>"\
            .format(id(self), self.mode, self.status, self.channel, self.command, self.format, self.data, self.id)


class MTRF64USBAdapter(object):
    _packetSize = 17
    _port = None
    _serial = Serial()

    def __init__(self, port: str):
        self._port = port

        self._serial.port = self._port
        self._serial.baudrate = 9600
        self._serial.timeout = 3

    def open(self):
        self._serial.open()

    def close(self):
        self._serial.close()

    def read_response(self) -> Response:
        data = self._serial.read(self._packetSize)
        response = self._parse(data)
        print("Receive:\n - packet: {0},\n - response: {1}".format(data, response))
        return response

    def send_request(self, request: Request) -> [Response]:
        responses = []

        data = self._build(request)
        print("Send:\n - request: {0},\n - packet: {1}".format(request, data))

        try:
            self._serial.write(data)

            response = self.read_response()
            responses.append(response)

            while response.count > 0:
                response = self.read_response()
                responses.append(response)

        except ResponseException:
            raise

        return responses

    def _crc(self, data) -> int:
        sum = 0
        for i in range(0, len(data)):
            sum = sum + data[i]
        sum = sum & 0xFF
        return sum

    def _build(self, request: Request) -> bytes:
        data = Struct(">BBBBBBB4sI")
        packet = data.pack(171, request.mode, request.action, 0, request.channel, request.command, request.format, request.data, request.id)

        data_end = Struct("BB")
        packet_end = data_end.pack(self._crc(packet), 172)

        packet = packet + packet_end

        return packet

    def _parse(self, packet: bytes) -> Response:
        data = Struct(">BBBBBBB4sIBB")

        response = Response()
        start_byte, response.mode, response.status, response.count, response.channel, response.command, response.format, response.data, response.id, crc, stop_byte = data.unpack(packet)

        if (start_byte != 173) or (stop_byte != 174) or (crc != self._crc(packet[0:-2])):
            raise ResponseException("Invalid response")

        return response