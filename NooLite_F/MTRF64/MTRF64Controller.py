from NooLite_F import NooLiteFController, ModuleInfo, ModuleState, ModuleMode, BrightnessDirection, ModuleType, RemoteListener
from NooLite_F.MTRF64 import MTRF64USBAdapter, IncomingData, Command, Mode, Action, OutgoingData, ResponseCode
from threading import Thread

class ModuleInfoParser(object):
    @staticmethod
    def parse(response: IncomingData) -> ModuleInfo:
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
    _listener_map: {int: RemoteListener} = {}
    _listener_thread = None

    _mode_map = {
        ModuleType.NOOLITE: Mode.TX,
        ModuleType.NOOLITE_F: Mode.TX_F,
    }

    def __init__(self, port: str):
        self._adapter = MTRF64USBAdapter(port)

        self._listener_thread = Thread(target=self._read_from_remotes)
        self._listener_thread.daemon = True
        self._listener_thread.start()
        print("end init")

    # Private
    def _command_mode(self, module_type: ModuleType) -> Mode:
        return self._mode_map[module_type]

    def _send_module_command(self, channel: int, command: Command, broadcast, mode: Mode, command_data: bytearray = None, fmt: int = None) -> [(bool, ModuleInfo)]:
        data = OutgoingData()

        data.mode = mode
        data.channel = channel
        data.command = command
        if broadcast:
            data.action = Action.SEND_BROADCAST_COMMAND
        else:
            data.action = Action.SEND_COMMAND

        if command_data is not None:
            data.data = command_data

        if fmt is not None:
            data.format = fmt

        response = self._adapter.send(data)
        return self._handle_command_responses(response)

    @staticmethod
    def _handle_command_responses(responses: [IncomingData]) -> [(bool, ModuleInfo)]:
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

    # Listeners

    # Commands
    def off(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.OFF, broadcast, self._command_mode(module_type))

    def on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.ON, broadcast, self._command_mode(module_type))

    def temporary_on(self, channel: int, duration: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(2)
        data[0] = duration & 0x00FF
        data[1] = duration & 0xFF00
        return self._send_module_command(channel, Command.TEMPORARY_ON, broadcast, self._command_mode(module_type), data, 6)

    def enable_temporary_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 0
        return self._send_module_command(channel, Command.MODES, broadcast, self._command_mode(module_type), data, 1)

    def disable_temporary_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1
        return self._send_module_command(channel, Command.MODES, broadcast, self._command_mode(module_type), data, 1)

    def switch(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.SWITCH, broadcast, self._command_mode(module_type))

    def brightness_tune(self, channel: int, direction: BrightnessDirection, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        if direction == BrightnessDirection.UP:
            command = Command.BRIGHT_UP
        else:
            command = Command.BRIGHT_DOWN
        return self._send_module_command(channel, command, broadcast, self._command_mode(module_type))

    def brightness_tune_back(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.BRIGHT_BACK, broadcast, self._command_mode(module_type))

    def brightness_tune_stop(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.STOP_BRIGHT, broadcast, self._command_mode(module_type))

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

        return self._send_module_command(channel, Command.BRIGHT_REG, broadcast, self._command_mode(module_type), data, 1)

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

        return self._send_module_command(channel, command, broadcast, self._command_mode(module_type), data, fmt)

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

        return self._send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_type), data, 1)

    def roll_rgb_color(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.ROLL_COLOR, broadcast, self._command_mode(module_type))

    def switch_rgb_color(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.SWITCH_COLOR, broadcast, self._command_mode(module_type))

    def switch_rgb_mode(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.SWITCH_MODE, broadcast, self._command_mode(module_type))

    def switch_rgb_mode_speed(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.SPEED_MODE, broadcast, self._command_mode(module_type))

    def set_rgb_brightness(self, channel: int, red: float, green: float, blue: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(3)
        data[0] = self._convert_color_brightness(red)
        data[1] = self._convert_color_brightness(green)
        data[2] = self._convert_color_brightness(blue)
        return self._send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_type), data, 3)

    def load_preset(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.LOAD_PRESET, broadcast, self._command_mode(module_type))

    def save_preset(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.SAVE_PRESET, broadcast, self._command_mode(module_type))

    def read_state(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.READ_STATE, broadcast, self._command_mode(module_type))

    def bind(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.BIND, broadcast, self._command_mode(module_type))

    def unbind(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.UNBIND, broadcast, self._command_mode(module_type))

    def service_mode_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1
        return self._send_module_command(channel, Command.SERVICE, broadcast, self._command_mode(module_type), data)

    def service_mode_off(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(channel, Command.SERVICE, broadcast, self._command_mode(module_type))

    def set_listener(self, channel: int, listener: RemoteListener):
        self._listener_map[channel] = listener
        print(self._listener_map)

    def _read_from_remotes(self):
        while True:
            input_data = self._adapter.get()

            listener: RemoteListener = self._listener_map.get(input_data.channel, None)

            if listener is not None:

                if input_data.command == Command.ON:
                    listener.on()
                elif input_data.command == Command.OFF:
                    listener.off()
                elif input_data.command == Command.SWITCH:
                    listener.switch()
                elif input_data.command == Command.TEMPORARY_ON:
                    if input_data.format == 5:
                        delay = input_data.data[0]
                    else:
                        delay = input_data.data[0] + (input_data.data[1] << 15)
                    listener.temporary_on(delay)
                elif input_data.command == Command.BRIGHT_UP:
                    listener.brightness_tune(BrightnessDirection.UP)
                elif input_data.command == Command.BRIGHT_DOWN:
                    listener.brightness_tune(BrightnessDirection.DOWN)
                elif input_data.command == Command.BRIGHT_BACK:
                    listener.brightness_tune_back()
                elif input_data.command == Command.BRIGHT_STEP_UP:
                    if input_data.format == 1:
                        step = input_data.data[0]
                    else:
                        step = None
                    listener.brightness_tune_step(BrightnessDirection.UP, step)
                elif input_data.command == Command.BRIGHT_STEP_DOWN:
                    if input_data.format == 1:
                        step = input_data.data[0]
                    else:
                        step = None
                    listener.brightness_tune_step(BrightnessDirection.DOWN, step)
                elif input_data.command == Command.STOP_BRIGHT:
                    listener.brightness_tune_stop()
                elif input_data.command == Command.SET_BRIGHTNESS:
                    if input_data.format == 3:
                        red = input_data.data[0] / 255
                        green = input_data.data[1] / 255
                        blue = input_data.data[2] / 255
                        listener.set_rgb_brightness(red, green, blue)
                    elif input_data.format == 1:
                        level = (input_data.data[0] - 35) / 120
                        if level < 0:
                            level = 0
                        elif level > 1:
                            level = 1
                        listener.set_brightness(level)
                elif input_data.command == Command.LOAD_PRESET:
                    listener.load_preset()
                elif input_data.command == Command.SAVE_PRESET:
                    listener.save_preset()
                elif input_data.command == Command.ROLL_COLOR:
                    listener.roll_rgb_color()
                elif input_data.command == Command.SWITCH_COLOR:
                    listener.switch_rgb_color()
                elif input_data.command == Command.SWITCH_MODE:
                    listener.switch_rgb_mode()
                elif input_data.command == Command.SPEED_MODE:
                    listener.switch_rgb_mode_speed()
