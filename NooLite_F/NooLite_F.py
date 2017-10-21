

from enum import IntEnum
from serial import Serial


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
    UNBIND = 7,
    SEND_COMMAND_BY_ADDRESS = 8


class ModuleState(IntEnum):
    OFF = 0,
    ON = 1,
    TEMPORARY_ON = 2


class ModuleMode(IntEnum):
    BIND_OFF = 0,
    BIND_ON = 1,


class BrightnessDirection(IntEnum):
    UP = 0,
    DOWN = 1,


class Request(object):
    mode: Mode = Mode.TX_F
    action: Action = Action.SEND_COMMAND
    channel: int = 0
    command: Command = Command.OFF
    format: int = 0
    data: bytearray = bytearray()
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


# TODO: replace format with enum or constants???

class NooLiteF(object):

    adapter = None

    def __init__(self, port: str):
        self.adapter = Adapter(port)

    def off(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.OFF, broadcast, mode)
        return self.handle_command_responses(responses)

    def on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.ON, broadcast, mode)
        return self.handle_command_responses(responses)

    # duration measurement equals 5 sec.
    def temporary_on(self, channel: int, duration: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(2)
        data[0] = duration & 0x00FF
        data[1] = duration & 0xFF00

        responses = self.send_module_command(channel, Command.TEMPORARY_ON, broadcast, mode, data, 6)
        return self.handle_command_responses(responses)

    def enable_temporary_on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 0

        responses = self.send_module_command(channel, Command.MODES, broadcast, mode, data, 1)
        return self.handle_command_responses(responses)

    def disable_temporary_on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1

        responses = self.send_module_command(channel, Command.MODES, broadcast, mode, data, 1)
        return self.handle_command_responses(responses)

    def switch(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SWITCH, broadcast, mode)
        return self.handle_command_responses(responses)

    def bright_tune(self, channel: int, direction: BrightnessDirection, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        if direction == BrightnessDirection.UP:
            command = Command.BRIGHT_UP
        else:
            command = Command.BRIGHT_DOWN

        responses = self.send_module_command(channel, command, broadcast, mode)
        return self.handle_command_responses(responses)

    def bright_tune_back(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.BRIGHT_BACK, broadcast, mode)
        return self.handle_command_responses(responses)

    def bright_tune_stop(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.STOP_BRIGHT, broadcast, mode)
        return self.handle_command_responses(responses)

    # speed in range from (0 .. 1.0)
    def bright_tune_custom(self, channel: int, direction: BrightnessDirection, speed: float, broadcast: bool = False, mode: Mode = Mode.TX_F):

        if speed >= 1:
            value = 127
        elif speed <= 0:
            value = 0
        else:
            value = int(speed * 127)

        if direction == BrightnessDirection.DOWN:
            value = -value - 1

        data: bytearray = bytearray(1)
        data[0] = value & 0xFF

        responses = self.send_module_command(channel, Command.BRIGHT_REG, broadcast, mode, data, 1)
        return self.handle_command_responses(responses)

    # step in microseconds if specify then can have values in range (1..255) or 0 (it is means 256), by default step equals 64
    def bright_step(self, channel: int, direction: BrightnessDirection, step: int = None, broadcast: bool = False, mode: Mode = Mode.TX_F):
        data: bytearray = None
        fmt: int = None

        if step is not None:
            fmt = 1
            data: bytearray = bytearray(1)
            data[0] = step

        if direction == BrightnessDirection.UP:
            command = Command.BRIGHT_STEP_UP
        else:
            command = Command.BRIGHT_STEP_DOWN

        responses = self.send_module_command(channel, command, broadcast, mode, data, fmt)
        return self.handle_command_responses(responses)

    # brightness value is float value in range 0 .. 1.0
    def set_brightness(self, channel: int, bright: float, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        if bright >= 1:
            value = 255
        elif bright <= 0:
            value = 0
        else:
            value = 35 + int(120 * bright)

        print(value)

        data: bytearray = bytearray(1)
        data[0] = value

        responses = self.send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, mode, data, 1)
        return self.handle_command_responses(responses)

    def roll_rgb_color(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.ROLL_COLOR, broadcast, mode)
        return self.handle_command_responses(responses)

    def switch_rgb_color(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SWITCH_COLOR, broadcast, mode)
        return self.handle_command_responses(responses)

    def switch_rgb_mode(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SWITCH_MODE, broadcast, mode)
        return self.handle_command_responses(responses)

    def speed_rgb_mode(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SPEED_MODE, broadcast, mode)
        return self.handle_command_responses(responses)

    # brightness value is float value in range 0 .. 1.0
    def set_rgb_brightness(self, channel: int, red: float, green: float, blue: float, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:

        data: bytearray = bytearray(3)
        data[0] = self.convert_color_bright(red)
        data[1] = self.convert_color_bright(green)
        data[2] = self.convert_color_bright(blue)

        responses = self.send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, mode, data, 3)
        return self.handle_command_responses(responses)

    def load_preset(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.LOAD_PRESET, broadcast, mode)
        return self.handle_command_responses(responses)

    def save_preset(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SAVE_PRESET, broadcast, mode)
        return self.handle_command_responses(responses)

    def read_state(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.READ_STATE, broadcast, mode)
        return self.handle_command_responses(responses)

    def bind(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.BIND, broadcast, mode)
        return self.handle_command_responses(responses)

    def unbind(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.UNBIND, broadcast, mode)
        return self.handle_command_responses(responses)

    def service_mode_on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1

        responses = self.send_module_command(channel, Command.SERVICE, broadcast, mode, data)
        return self.handle_command_responses(responses)

    def service_mode_off(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        responses = self.send_module_command(channel, Command.SERVICE, broadcast, mode)
        return self.handle_command_responses(responses)

    def send_module_command(self, channel: int, command: Command, broadcast, mode: Mode, data: bytearray = None, fmt: int = None) -> [Response]:
        request = Request()

        request.mode = mode
        request.channel = channel
        request.command = command
        if broadcast:
            request.action = Action.SEND_BROADCAST_COMMAND
        else:
            request.action = Action.SEND_COMMAND

        if data is not None:
            request.data = data

        if fmt is not None:
            request.format = fmt

        responses = self.send_request(request)
        return responses

    def send_request(self, request: Request) -> [Response]:
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

    def convert_color_bright(self, bright: float) -> int:
        if bright >= 1:
            value = 255
        elif bright <= 0:
            value = 0
        else:
            value = int(255 * bright)

        return value
