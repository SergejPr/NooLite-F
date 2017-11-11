from NooLite_F import NooLiteFController, ModuleInfo, ModuleState, ModuleMode, BrightnessDirection, ModuleType, RemoteListener, BatteryState
from NooLite_F.MTRF64 import MTRF64USBAdapter, IncomingData, Command, Mode, Action, OutgoingData, ResponseCode


class OutgoingDataException(Exception):
    """Base class for response exceptions."""


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

    _mode_map = {
        ModuleType.NOOLITE: Mode.TX,
        ModuleType.NOOLITE_F: Mode.TX_F,
    }

    def __init__(self, port: str):
        self._adapter = MTRF64USBAdapter(port)
        self._adapter.set_listener(self._on_receive)

    # Private
    def _command_mode(self, module_type: ModuleType) -> Mode:
        return self._mode_map[module_type]

    def _send_module_command(self, module_id, channel: int, command: Command, broadcast, mode: Mode, command_data: bytearray = None, fmt: int = None) -> [(bool, ModuleInfo)]:
        data = OutgoingData()

        data.mode = mode
        data.command = command

        if module_id is not None:
            data.id = module_id
            if channel is None:
                data.action = Action.SEND_COMMAND_TO_ID
            else:
                data.channel = channel
                data.action = Action.SEND_COMMAND_TO_ID_IN_CHANNEL
        elif channel is not None:
            data.channel = channel
            if broadcast and mode == Mode.TX_F: # Broadcast used only for NOOLITE-F mode
                data.action = Action.SEND_BROADCAST_COMMAND
            else:
                data.action = Action.SEND_COMMAND
        else:
            raise OutgoingDataException("Module_id and channel are not specified. You must specify at least one of them.")

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

    # Commands
    def off(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.OFF, broadcast, self._command_mode(module_type))

    def on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.ON, broadcast, self._command_mode(module_type))

    def temporary_on(self, duration: int, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(2)
        data[0] = duration & 0x00FF
        data[1] = duration & 0xFF00
        return self._send_module_command(module_id, channel, Command.TEMPORARY_ON, broadcast, self._command_mode(module_type), data, 6)

    def enable_temporary_on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 0
        return self._send_module_command(module_id, channel, Command.MODES, broadcast, self._command_mode(module_type), data, 1)

    def disable_temporary_on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1
        return self._send_module_command(module_id, channel, Command.MODES, broadcast, self._command_mode(module_type), data, 1)

    def switch(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.SWITCH, broadcast, self._command_mode(module_type))

    def brightness_tune(self, direction: BrightnessDirection, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        if direction == BrightnessDirection.UP:
            command = Command.BRIGHT_UP
        else:
            command = Command.BRIGHT_DOWN
        return self._send_module_command(module_id, channel, command, broadcast, self._command_mode(module_type))

    def brightness_tune_back(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.BRIGHT_BACK, broadcast, self._command_mode(module_type))

    def brightness_tune_stop(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.STOP_BRIGHT, broadcast, self._command_mode(module_type))

    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
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

        return self._send_module_command(module_id, channel, Command.BRIGHT_REG, broadcast, self._command_mode(module_type), data, 1)

    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
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

        return self._send_module_command(module_id, channel, command, broadcast, self._command_mode(module_type), data, fmt)

    def set_brightness(self, brightness: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        if brightness >= 1:
            value = 255
        elif brightness <= 0:
            value = 0
        else:
            value = 35 + int(120 * brightness)

        print(value)

        data: bytearray = bytearray(1)
        data[0] = value

        return self._send_module_command(module_id, channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_type), data, 1)

    def roll_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.ROLL_COLOR, broadcast, self._command_mode(module_type))

    def switch_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.SWITCH_COLOR, broadcast, self._command_mode(module_type))

    def switch_rgb_mode(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.SWITCH_MODE, broadcast, self._command_mode(module_type))

    def switch_rgb_mode_speed(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.SPEED_MODE, broadcast, self._command_mode(module_type))

    def set_rgb_brightness(self, red: float, green: float, blue: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(3)
        data[0] = self._convert_color_brightness(red)
        data[1] = self._convert_color_brightness(green)
        data[2] = self._convert_color_brightness(blue)
        return self._send_module_command(module_id, channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_type), data, 3)

    def load_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.LOAD_PRESET, broadcast, self._command_mode(module_type))

    def save_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.SAVE_PRESET, broadcast, self._command_mode(module_type))

    def read_state(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.READ_STATE, broadcast, self._command_mode(module_type))

    def bind(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.BIND, broadcast, self._command_mode(module_type))

    def unbind(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.UNBIND, broadcast, self._command_mode(module_type))

    def service_mode_on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        data: bytearray = bytearray(1)
        data[0] = 1
        return self._send_module_command(module_id, channel, Command.SERVICE, broadcast, self._command_mode(module_type), data)

    def service_mode_off(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        return self._send_module_command(module_id, channel, Command.SERVICE, broadcast, self._command_mode(module_type))

    def set_listener(self, channel: int, listener: RemoteListener):
        self._listener_map[channel] = listener
        print(self._listener_map)

    # Listeners
    def _on_receive(self, incoming_data: IncomingData):
        listener: RemoteListener = self._listener_map.get(incoming_data.channel, None)

        if listener is not None:

            if incoming_data.command == Command.ON:
                listener.on_on()
            elif incoming_data.command == Command.OFF:
                listener.on_off()
            elif incoming_data.command == Command.SWITCH:
                listener.on_switch()
            elif incoming_data.command == Command.TEMPORARY_ON:
                if incoming_data.format == 5:
                    delay = incoming_data.data[0]
                else:
                    delay = incoming_data.data[0] + (incoming_data.data[1] << 15)
                listener.on_temporary_on(delay)
            elif incoming_data.command == Command.BRIGHT_UP:
                listener.on_brightness_tune(BrightnessDirection.UP)
            elif incoming_data.command == Command.BRIGHT_DOWN:
                listener.on_brightness_tune(BrightnessDirection.DOWN)
            elif incoming_data.command == Command.BRIGHT_BACK:
                listener.on_brightness_tune_back()
            elif incoming_data.command == Command.BRIGHT_STEP_UP:
                if incoming_data.format == 1:
                    step = incoming_data.data[0]
                else:
                    step = None
                listener.on_brightness_tune_step(BrightnessDirection.UP, step)
            elif incoming_data.command == Command.BRIGHT_STEP_DOWN:
                if incoming_data.format == 1:
                    step = incoming_data.data[0]
                else:
                    step = None
                listener.on_brightness_tune_step(BrightnessDirection.DOWN, step)
            elif incoming_data.command == Command.STOP_BRIGHT:
                listener.on_brightness_tune_stop()
            elif incoming_data.command == Command.SET_BRIGHTNESS:
                if incoming_data.format == 3:
                    red = incoming_data.data[0] / 255
                    green = incoming_data.data[1] / 255
                    blue = incoming_data.data[2] / 255
                    listener.on_set_rgb_brightness(red, green, blue)
                elif incoming_data.format == 1:
                    level = (incoming_data.data[0] - 35) / 120
                    if level < 0:
                        level = 0
                    elif level > 1:
                        level = 1
                    listener.on_set_brightness(level)
            elif incoming_data.command == Command.LOAD_PRESET:
                listener.on_load_preset()
            elif incoming_data.command == Command.SAVE_PRESET:
                listener.on_save_preset()
            elif incoming_data.command == Command.ROLL_COLOR:
                listener.on_roll_rgb_color()
            elif incoming_data.command == Command.SWITCH_COLOR:
                listener.on_switch_rgb_color()
            elif incoming_data.command == Command.SWITCH_MODE:
                listener.on_switch_rgb_mode()
            elif incoming_data.command == Command.SPEED_MODE:
                listener.on_switch_rgb_mode_speed()
            elif incoming_data.command == Command.BRIGHT_REG:
                if incoming_data.format == 1:
                    if incoming_data.data[0] & 0x80 == 0x80:
                        direction = BrightnessDirection.UP
                    else:
                        direction = BrightnessDirection.DOWN
                    speed = (incoming_data.data[0] & 0x7F) / 127
                    listener.on_brightness_tune_custom(direction, speed)
            elif incoming_data.command == Command.SENS_TEMP_HUMI:
                # really from PT111 I get fmt = 7, but in specs is specify that fmt should be 3

                if incoming_data.format == 7:

                    battery_bit = (incoming_data.data[1] & 0x80) >> 7
                    if battery_bit:
                        battery = BatteryState.LOW
                    else:
                        battery = BatteryState.OK

                    temp_low = incoming_data.data[0]
                    temp_hi = incoming_data.data[1] & 0x0F
                    temp = (temp_hi << 8) + temp_low
                    if temp > 0x0800:
                        temp = -(0x1000 - temp)
                    temp = temp / 10

                    device_type = (incoming_data.data[1] & 0x70) >> 4
                    if device_type == 2:
                        humi = incoming_data.data[2]
                    else:
                        humi = None

                    analog = incoming_data.data[3] / 255

                    listener.on_temp_humi(temp, humi, battery, analog)


