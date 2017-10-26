
from NooLite_F import NooLiteFController, ModuleInfo, ModuleState, ModuleMode, BrightnessDirection, ModuleType
from NooLite_F.MTRF64 import MTRF64USBAdapter, Response, Command, Mode, Action, Request, ResponseCode


class ModuleInfoParser(object):
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


class MTRF64Controller(NooLiteFController):

    _adapter = None

    _mode_map = {
        ModuleType.NOOLITE: Mode.TX,
        ModuleType.NOOLITE_F: Mode.TX_F,
    }

    def __init__(self, port: str):
        self._adapter = MTRF64USBAdapter(port)

    def _command_mode(self, module_type: ModuleType) -> Mode:
        return self._mode_map[module_type]

    def _send_module_command(self, channel: int, command: Command, broadcast, mode: Mode, data: bytearray = None, fmt: int = None) -> [Response]:
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

        responses = self._send_request(request)
        return responses

    @staticmethod
    def _handle_command_responses(responses: [Response]) -> [(bool, ModuleInfo)]:
        results = []
        for response in responses:
            info = ModuleInfoParser.parse(response)
            status = response.status == ResponseCode.SUCCESS or response.status == ResponseCode.BIND_SUCCESS
            results.append((status, info))

        return results

    @staticmethod
    def _convert_color_brightness(bright: float) -> int:
        if bright >= 1:
            value = 255
        elif bright <= 0:
            value = 0
        else:
            value = int(255 * bright)

        return value

    def _send_request(self, request: Request) -> [Response]:
        self._adapter.open()
        response = self._adapter.send_request(request)
        self._adapter.close()
        return response

    def off(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.OFF, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.ON, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def temporary_on(self, channel: int, duration: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(2)
        data[0] = duration & 0x00FF
        data[1] = duration & 0xFF00

        responses = self._send_module_command(channel, Command.TEMPORARY_ON, broadcast, self._command_mode(module_type), data, 6)
        return self._handle_command_responses(responses)

    def enable_temporary_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 0

        responses = self._send_module_command(channel, Command.MODES, broadcast, self._command_mode(module_type), data, 1)
        return self._handle_command_responses(responses)

    def disable_temporary_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1

        responses = self._send_module_command(channel, Command.MODES, broadcast, self._command_mode(module_type), data, 1)
        return self._handle_command_responses(responses)

    def switch(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.SWITCH, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def brightness_tune(self, channel: int, direction: BrightnessDirection, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        if direction == BrightnessDirection.UP:
            command = Command.BRIGHT_UP
        else:
            command = Command.BRIGHT_DOWN

        responses = self._send_module_command(channel, command, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def brightness_tune_back(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.BRIGHT_BACK, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def brightness_tune_stop(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.STOP_BRIGHT, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def brightness_tune_custom(self, channel: int, direction: BrightnessDirection, speed: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F):
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

        responses = self._send_module_command(channel, Command.BRIGHT_REG, broadcast, self._command_mode(module_type), data, 1)
        return self._handle_command_responses(responses)

    def brightness_tune_step(self, channel: int, direction: BrightnessDirection, step: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F):
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

        responses = self._send_module_command(channel, command, broadcast, self._command_mode(module_type), data, fmt)
        return self._handle_command_responses(responses)

    def set_brightness(self, channel: int, brightness: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        if brightness >= 1:
            value = 255
        elif brightness <= 0:
            value = 0
        else:
            value = 35 + int(120 * brightness)

        print(value)

        data: bytearray = bytearray(1)
        data[0] = value

        responses = self._send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_type), data, 1)
        return self._handle_command_responses(responses)

    def roll_rgb_color(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.ROLL_COLOR, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def switch_rgb_color(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.SWITCH_COLOR, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def switch_rgb_mode(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.SWITCH_MODE, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def switch_rgb_mode_speed(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.SPEED_MODE, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def set_rgb_brightness(self, channel: int, red: float, green: float, blue: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(3)
        data[0] = self._convert_color_brightness(red)
        data[1] = self._convert_color_brightness(green)
        data[2] = self._convert_color_brightness(blue)

        responses = self._send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_type), data, 3)
        return self._handle_command_responses(responses)

    def load_preset(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.LOAD_PRESET, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def save_preset(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.SAVE_PRESET, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def read_state(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.READ_STATE, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def bind(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.BIND, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def unbind(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.UNBIND, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)

    def service_mode_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1

        responses = self._send_module_command(channel, Command.SERVICE, broadcast, self._command_mode(module_type), data)
        return self._handle_command_responses(responses)

    def service_mode_off(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        responses = self._send_module_command(channel, Command.SERVICE, broadcast, self._command_mode(module_type))
        return self._handle_command_responses(responses)
