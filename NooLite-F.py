

from enum import IntEnum
from serial import Serial


class Command(IntEnum):
    OFF = 0,
    ON = 2,
    SWITCH = 4,
    SET_BRIGHTNESS = 6,
    LOAD_PRESET = 7,
    READ_STATE = 128,
    SEND_STATE = 130


class Mode(IntEnum):
    TX = 0,
    RX = 1,
    TX_F = 2,
    RX_F = 3,
    SERVICE = 4,
    UPDATE = 5


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
    UNBIND = 7,
    SEND_COMMAND_BY_ADDRESS = 8


class ModuleState(IntEnum):
    OFF = 0,
    ON = 1,
    TEMPORARY_ON = 2


class ModuleMode(IntEnum):
    BIND_OFF = 0,
    BIND_ON = 1,


class Request(object):
    mode: Mode = Mode.TX_F
    action: Action = Action.SEND_COMMAND
    channel: int = 0
    command: Command = Command.OFF
    format: int = 0
    data: bytearray = bytearray()
    id: int = 0

    def __repr__(self):
        return "<Request (0x{0:x}), mode: {1}, action: {2}, channel: {3}, command: {4}, format: {5}, data: {6}, id: 0x{7:x}>"\
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
        return "<Response (0x{0:x}), mode: {1}, status: {2}, channel: {3}, command: {4}, format: {5}, data: {6}, id: 0x{7:x}>"\
            .format(id(self), self.mode, self.status, self.channel, self.command, self.format, self.data, self.id)


class ModuleInfo(object):
    state: ModuleState
    mode: ModuleMode
    brightness: float = None
    id: int = None
    firmware: int = None
    type: int = None

    def __repr__(self):
        return "<ModuleInfo (0x{0:x}), id: 0x{1:x}, type: {2}, firmware: {3}, state: {4}, brightness: {5}, mode: {6}>"\
            .format(id(self), self.id, self.type, self.firmware, self.state, self.brightness, self.mode)


class PacketUtils:
    @staticmethod
    def crc(data):
        sum = 0
        for i in range(0, len(data) - 2):
            sum = sum + data[i]
        sum = sum & 0xFF
        return sum


class RequestPacketBuilder:
    START_BYTE = 171
    STOP_BYTE = 172

    PACKET_SIZE = 17

    ST = 0
    MODE = 1
    CTR = 2
    CH = 4
    CMD = 5
    FMT = 6
    D0 = 7
    D1 = 8
    D2 = 9
    D3 = 10
    ID0 = 11
    ID1 = 12
    ID2 = 13
    ID3 = 14
    CRC = 15
    SP = 16

    @staticmethod
    def build(request: Request) -> bytearray:
        data = bytearray(RequestPacketBuilder.PACKET_SIZE)

        data[RequestPacketBuilder.ST] = RequestPacketBuilder.START_BYTE
        data[RequestPacketBuilder.MODE] = request.mode.value
        data[RequestPacketBuilder.CTR] = request.action.value
        data[RequestPacketBuilder.CH] = request.channel
        data[RequestPacketBuilder.CMD] = request.command.value
        data[RequestPacketBuilder.FMT] = request.format
        if len(request.data) >= 1:
            data[RequestPacketBuilder.D0] = request.data[0]
        if len(request.data) >= 2:
            data[RequestPacketBuilder.D1] = request.data[1]
        if len(request.data) >= 3:
            data[RequestPacketBuilder.D2] = request.data[2]
        if len(request.data) >= 4:
            data[RequestPacketBuilder.D3] = request.data[3]
        data[RequestPacketBuilder.ID0] = request.id & 0xFF000000
        data[RequestPacketBuilder.ID1] = request.id & 0x00FF0000
        data[RequestPacketBuilder.ID2] = request.id & 0x0000FF00
        data[RequestPacketBuilder.ID3] = request.id & 0x000000FF
        data[RequestPacketBuilder.CRC] = PacketUtils.crc(data)
        data[RequestPacketBuilder.SP] = RequestPacketBuilder.STOP_BYTE

        return data


class ResponseException(Exception):
    """Base class for response exceptions."""


class ResponsePacketParser:
    START_BYTE = 173
    STOP_BYTE = 174

    PACKET_SIZE = 17

    ST = 0
    MODE = 1
    CTR = 2
    TOGL = 3
    CH = 4
    CMD = 5
    FMT = 6
    D0 = 7
    D1 = 8
    D2 = 9
    D3 = 10
    ID0 = 11
    ID1 = 12
    ID2 = 13
    ID3 = 14
    CRC = 15
    SP = 16

    @staticmethod
    def parse(data: bytearray) -> Response:
        if (len(data) != ResponsePacketParser.PACKET_SIZE or data[ResponsePacketParser.ST] != ResponsePacketParser.START_BYTE) or (data[ResponsePacketParser.SP] != ResponsePacketParser.STOP_BYTE) or (data[ResponsePacketParser.CRC] != PacketUtils.crc(data)):
            raise ResponseException("Invalid response")

        response = Response()

        response.mode = Mode(data[ResponsePacketParser.MODE])
        response.status = ResponseCode(data[ResponsePacketParser.CTR])
        response.command = Command(data[ResponsePacketParser.CMD])
        response.channel = data[ResponsePacketParser.CH]
        response.count = data[ResponsePacketParser.TOGL]
        response.format = data[ResponsePacketParser.FMT]
        response.data = bytearray(4)
        response.data[0] = data[ResponsePacketParser.D0]
        response.data[1] = data[ResponsePacketParser.D1]
        response.data[2] = data[ResponsePacketParser.D2]
        response.data[3] = data[ResponsePacketParser.D3]
        response.id = (data[ResponsePacketParser.ID0] << 24) + (data[ResponsePacketParser.ID1] << 16) + (data[ResponsePacketParser.ID2] << 8) + data[ResponsePacketParser.ID3]

        return response


class ModuleInfoParser:
    @staticmethod
    def parse(response: Response) -> ModuleInfo:
        info = None
        if response.command == Command.SEND_STATE:
            info = ModuleInfo()
            info.type = response.data[0]
            info.firmware = response.data[1]
            info.id = response.id

            if response.format == 0:
                info.state = ModuleState(response.data[2] & 0x0F)
                info.mode = ModuleMode(response.data[2] & 0x80)
                info.brightness = response.data[3] / 255

        return info


class Adapter(object):
    port = None
    serial = Serial()

    def __init__(self, port: str):
        self.port = port

    def open(self):
        self.serial.port = self.port
        self.serial.baudrate = 9600
        self.serial.timeout = 3
        self.serial.open()

    def close(self):
        self.serial.close()

    def read_response(self) -> Response:
        data = self.serial.read(ResponsePacketParser.PACKET_SIZE)
        response = ResponsePacketParser.parse(data)
        print("Receive:\n - packet: {0},\n - response: {1}".format(data, response))
        return response

    def send_request(self, request: Request):
        responses = []

        data = RequestPacketBuilder.build(request)
        print("Send:\n - request: {0},\n - packet: {1}".format(request, data))

        try:
            self.serial.write(data)

            response = self.read_response()
            responses.append(response)

            while response.count > 0:
                response = self.read_response()
                responses.append(response)

        except ResponseException:
            raise

        return responses


class NooLiteF(object):

    adapter = None

    def __init__(self, port: str):
        self.adapter = Adapter(port)

    def on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.ON, broadcast, mode)
        return self.handle_command_responses(responses)

    def off(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.OFF, broadcast, mode)
        return self.handle_command_responses(responses)

    def switch(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SWITCH, broadcast, mode)
        return self.handle_command_responses(responses)

    def load_preset(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.LOAD_PRESET, broadcast, mode)
        return self.handle_command_responses(responses)

    def read_state(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.READ_STATE, broadcast, mode)
        return self.handle_command_responses(responses)

    def set_brightness(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, mode)
        return self.handle_command_responses(responses)

    def send_module_command(self, channel: int, command: Command, broadcast, mode: Mode) -> [Response]:
        request = Request()

        request.mode = mode
        if broadcast:
            request.action = Action.SEND_BROADCAST_COMMAND
        else:
            request.action = Action.SEND_COMMAND

        request.channel = channel
        request.command = command

        self.adapter.open()

        responses = self.adapter.send_request(request)

        self.adapter.close()
        return responses

    def handle_command_responses(self, responses) -> [(bool, ModuleInfo)]:
        results = []
        for response in responses:
            info = ModuleInfoParser.parse(response)
            status = response.status == ResponseCode.SUCCESS or response.status == ResponseCode.BIND_SUCCESS
            results.append((status, info))

        return results
