from NooLite_F import NooLiteFController, Direction, ModuleMode, NooLiteFListener, BatteryState
from NooLite_F import ModuleInfo, ModuleBaseStateInfo, ModuleExtraStateInfo, ModuleChannelsStateInfo, ModuleState, ServiceModeState, DimmerCorrectionConfig, ModuleConfig
from NooLite_F import NooliteModeState, InputMode
from NooLite_F import ResponseBaseInfo, ResponseExtraInfo, ResponseChannelsInfo, ResponseModuleConfig, ResponseDimmerCorrectionConfig
from NooLite_F.MTRF64 import IncomingData, Command, Mode, Action, OutgoingData, ResponseCode, MTRF64Adapter
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Tuple


T = TypeVar('T')
V = TypeVar('V')


class OutgoingDataException(Exception):
    """Base class for response exceptions."""
    pass


class Parser(ABC, Generic[T, V]):
    @abstractmethod
    def parse(self, data: T) -> V:
        pass


class ModuleInfoParser(Parser[IncomingData, ModuleInfo]):
    def parse(self, data: IncomingData) -> ModuleInfo:
        info = None
        if data.command == Command.SEND_STATE and (data.format in (0, 1, 2)):
            info = ModuleInfo()
            info.type = data.data[0]
            info.firmware = data.data[1]
            info.id = data.id

        return info


class ModuleBaseStateInfoParser(Parser[IncomingData, ModuleBaseStateInfo]):
    def parse(self, data: IncomingData) -> ModuleBaseStateInfo:
        info = None
        if data.command == Command.SEND_STATE and data.format == 0:
            info = ModuleBaseStateInfo()

            states = {
                0: ModuleState.OFF,
                1: ModuleState.ON,
                2: ModuleState.TEMPORARY_ON,
            }

            state = data.data[2]

            if state in states:
                info.state = states[state]

            if (data.data[2] & 0x80) == 0x80:
                info.service_mode = ServiceModeState.BIND_ON
            else:
                info.service_mode = ServiceModeState.BIND_OFF

            info.brightness = data.data[3] / 255

        return info


class ModuleExtraStateInfoParser(Parser[IncomingData, ModuleExtraStateInfo]):
    def parse(self, data: IncomingData) -> ModuleExtraStateInfo:
        info = None
        if data.command == Command.SEND_STATE and data.format == 1:
            info = ModuleExtraStateInfo()
            info.extra_input_state = (data.data[2] > 0)

            if (data.data[3] & 0x02) == 0x02:
                info.noolite_mode_state = NooliteModeState.DISABLED
            elif (data.data[3] & 0x01) == 0x01:
                info.noolite_mode_state = NooliteModeState.TEMPORARY_DISABLED
            else:
                info.noolite_mode_state = NooliteModeState.ENABLED

        return info


class ModuleChannelsInfoParser(Parser[IncomingData, ModuleChannelsStateInfo]):
    def parse(self, data: IncomingData) -> ModuleChannelsStateInfo:
        info = None
        if data.command == Command.SEND_STATE and data.format == 2:
            info = ModuleChannelsStateInfo()
            info.noolite_cells = data.data[2]
            info.noolite_f_cells = data.data[3]

        return info


class ModuleConfigurationParser(Parser[IncomingData, ModuleConfig]):

    def state(self, data: int, bit_num: int) -> bool:
        return (data & 1 << bit_num) == (1 << bit_num)

    def parse(self, data: IncomingData) -> ModuleConfig:
        info = None
        if data.command == Command.SEND_STATE and data.format == 16:
            info = ModuleConfig()

            info.save_state_mode = self.state(data.data[0], 0)
            info.dimmer_mode = self.state(data.data[0], 1)
            info.noolite_support = self.state(data.data[0], 2)
            info.init_state = self.state(data.data[0], 5)
            info.noolite_retranslation = self.state(data.data[0], 6)

            extra_input_modes = {
                0: InputMode.SWITCH,
                1: InputMode.BUTTON,
                2: InputMode.BREAKER,
                3: InputMode.DISABLED,
            }

            extra_input_mode = (data.data[0] & 0x18) >> 3
            if extra_input_mode in extra_input_modes:
                info.input_mode = extra_input_modes[extra_input_mode]

        return info


class BrightnessConfigurationParser(Parser[IncomingData, ModuleConfig]):
    def parse(self, data: IncomingData) -> DimmerCorrectionConfig:
        info = None
        if data.command == Command.SEND_STATE and data.format == 17:
            info = DimmerCorrectionConfig()
            info.max_level = data.data[0] / 255
            info.min_level = data.data[1] / 255
        return info


class MTRF64Controller(NooLiteFController):

    _adapter = None
    _listener_map = {}

    _mode_map = {
        ModuleMode.NOOLITE: Mode.TX,
        ModuleMode.NOOLITE_F: Mode.TX_F,
    }

    def __init__(self, port: str):
        self._adapter = MTRF64Adapter(port, self._on_receive)

    def release(self):
        self._adapter.release()
        self._adapter = None
        self._listener_map = {}

    # Private
    def _command_mode(self, module_mode: ModuleMode) -> Mode:
        return self._mode_map[module_mode]

    def _send_module_command(self, module_id, channel: int, command: Command, broadcast, mode: Mode, command_data: bytearray = None, fmt: int = None) -> List[IncomingData]:
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
            if broadcast and mode == Mode.TX_F:  # Broadcast used only for NOOLITE-F mode
                data.action = Action.SEND_BROADCAST_COMMAND
            else:
                data.action = Action.SEND_COMMAND
        else:
            raise OutgoingDataException(
                "Module_id and channel are not specified. You must specify at least one of them.")

        if command_data is not None:
            data.data = command_data

        if fmt is not None:
            data.format = fmt

        return self._adapter.send(data)

    def _send_module_base_command(self, module_id, channel: int, command: Command, broadcast, mode: Mode, command_data: bytearray = None, fmt: int = None, parser: Parser[IncomingData, V] = ModuleBaseStateInfoParser()) -> List[Tuple[bool, ModuleInfo, V]]:
        response = self._send_module_command(module_id, channel, command, broadcast, mode, command_data, fmt)
        return self._handle_base_command_responses(response, parser)

    def _send_module_config_command(self, module_id, channel: int, command: Command, broadcast, mode: Mode, command_data: bytearray = None, fmt: int = None,  parser: Parser[IncomingData, V] = ModuleConfigurationParser()) -> List[Tuple[bool, V]]:
        response = self._send_module_command(module_id, channel, command, broadcast, mode, command_data, fmt)
        return self._handle_config_command_responses(response, parser)

    @staticmethod
    def _handle_base_command_responses(responses: List[IncomingData], parser: Parser[IncomingData, V]) -> List[Tuple[bool, ModuleInfo, V]]:
        results = []
        for response in responses:
            info = ModuleInfoParser().parse(response)
            extra_info = parser.parse(response)
            status = response.status == ResponseCode.SUCCESS or response.status == ResponseCode.BIND_SUCCESS
            results.append((status, info, extra_info))
        return results

    @staticmethod
    def _handle_config_command_responses(responses: List[IncomingData], parser: Parser[IncomingData, V]) -> List[Tuple[bool, V]]:
        results = []
        for response in responses:
            config = parser.parse(response)
            status = response.status == ResponseCode.SUCCESS or response.status == ResponseCode.BIND_SUCCESS
            results.append((status, config))
        return results

    @staticmethod
    def _convert_brightness(bright: float) -> int:
        if bright >= 1:
            value = 255
        elif bright <= 0:
            value = 0
        else:
            value = int((255 * bright) + 0.5)
        return value

    # Commands
    def off(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.OFF, broadcast, self._command_mode(module_mode))

    def on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.ON, broadcast, self._command_mode(module_mode))

    def temporary_on(self, duration: int, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        data = bytearray(2)
        data[0] = duration & 0x00FF
        data[1] = duration & 0xFF00
        return self._send_module_base_command(module_id, channel, Command.TEMPORARY_ON, broadcast, self._command_mode(module_mode), data, 6)

    def set_temporary_on_mode(self, enabled: bool, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        data = bytearray(1)
        if not enabled:
            data[0] = 1
        return self._send_module_base_command(module_id, channel, Command.MODES, broadcast, self._command_mode(module_mode), data, 1)

    def switch(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.SWITCH, broadcast, self._command_mode(module_mode))

    def brightness_tune(self, direction: Direction, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        if direction == Direction.UP:
            command = Command.BRIGHT_UP
        else:
            command = Command.BRIGHT_DOWN
        return self._send_module_base_command(module_id, channel, command, broadcast, self._command_mode(module_mode))

    def brightness_tune_back(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.BRIGHT_BACK, broadcast, self._command_mode(module_mode))

    def brightness_tune_stop(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.STOP_BRIGHT, broadcast, self._command_mode(module_mode))

    def brightness_tune_custom(self, direction: Direction, speed: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        if speed >= 1:
            value = 127
        elif speed <= 0:
            value = 0
        else:
            value = int((speed * 127) + 0.5)

        if direction == Direction.DOWN:
            value = -value - 1

        data = bytearray(1)
        data[0] = value & 0xFF

        return self._send_module_base_command(module_id, channel, Command.BRIGHT_REG, broadcast, self._command_mode(module_mode), data, 1)

    def brightness_tune_step(self, direction: Direction, step: int = None, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        data = None
        fmt = None

        if step is not None:
            fmt = 1
            data = bytearray(1)
            data[0] = step

        if direction == Direction.UP:
            command = Command.BRIGHT_STEP_UP
        else:
            command = Command.BRIGHT_STEP_DOWN

        return self._send_module_base_command(module_id, channel, command, broadcast, self._command_mode(module_mode), data, fmt)

    def set_brightness(self, brightness: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        if brightness >= 1:
            value = 155
        elif brightness <= 0:
            value = 0
        else:
            value = 35 + int((120 * brightness) + 0.5)

        data = bytearray(1)
        data[0] = value

        return self._send_module_base_command(module_id, channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_mode), data, 1)

    def roll_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.ROLL_COLOR, broadcast, self._command_mode(module_mode))

    def switch_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.SWITCH_COLOR, broadcast, self._command_mode(module_mode))

    def switch_rgb_mode(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.SWITCH_MODE, broadcast, self._command_mode(module_mode))

    def switch_rgb_mode_speed(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.SPEED_MODE, broadcast, self._command_mode(module_mode))

    def set_rgb_brightness(self, red: float, green: float, blue: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        data = bytearray(3)
        data[0] = self._convert_brightness(red)
        data[1] = self._convert_brightness(green)
        data[2] = self._convert_brightness(blue)
        return self._send_module_base_command(module_id, channel, Command.SET_BRIGHTNESS, broadcast, self._command_mode(module_mode), data, 3)

    def load_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.LOAD_PRESET, broadcast, self._command_mode(module_mode))

    def save_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.SAVE_PRESET, broadcast, self._command_mode(module_mode))

    def read_state(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.READ_STATE, broadcast, self._command_mode(module_mode))

    def read_extra_state(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseExtraInfo]:
        return self._send_module_base_command(module_id, channel, Command.READ_STATE, broadcast, self._command_mode(module_mode), fmt=1, parser=ModuleExtraStateInfoParser())

    def read_channels_state(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseChannelsInfo]:
        return self._send_module_base_command(module_id, channel, Command.READ_STATE, broadcast, self._command_mode(module_mode), fmt=2, parser=ModuleChannelsInfoParser())

    def read_module_config(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseModuleConfig]:
        return self._send_module_config_command(module_id, channel, Command.READ_STATE, broadcast, self._command_mode(module_mode), fmt=16, parser=ModuleConfigurationParser())

    def write_module_config(self, config: ModuleConfig, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseModuleConfig]:
        data = bytearray(4)

        save_state_mode = config.save_state_mode
        if save_state_mode is not None:
            data[2] = data[2] | 0x01
            if save_state_mode:
                data[0] = data[0] | 0x01

        dimmer_mode = config.dimmer_mode
        if dimmer_mode is not None:
            data[2] = data[2] | 0x02
            if dimmer_mode:
                data[0] = data[0] | 0x02

        noolite_support = config.noolite_support
        if noolite_support is not None:
            data[2] = data[2] | 0x04
            if noolite_support:
                data[0] = data[0] | 0x04

        input_mode = config.input_mode
        if input_mode is not None:
            data[2] = data[2] | 0x18
            if input_mode == InputMode.SWITCH:
                pass
            elif input_mode == InputMode.BUTTON:
                data[0] = data[0] | 0x08
            elif input_mode == InputMode.BREAKER:
                data[0] = data[0] | 0x10
            elif input_mode == InputMode.DISABLED:
                data[0] = data[0] | 0x18

        init_state = config.init_state
        if init_state is not None:
            data[2] = data[2] | 0x20
            if init_state:
                data[0] = data[0] | 0x20

        noolite_retranslation = config.noolite_retranslation
        if noolite_retranslation is not None:
            data[2] = data[2] | 0x40
            if noolite_retranslation:
                data[0] = data[0] | 0x40

        return self._send_module_config_command(module_id, channel, Command.WRITE_STATE, broadcast, self._command_mode(module_mode), data, fmt=16, parser=ModuleConfigurationParser())

    def read_dimmer_correction(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseDimmerCorrectionConfig]:
        return self._send_module_config_command(module_id, channel, Command.READ_STATE, broadcast, self._command_mode(module_mode), fmt=17, parser=BrightnessConfigurationParser())

    def write_dimmer_correction(self, config: DimmerCorrectionConfig, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseDimmerCorrectionConfig]:
        data = bytearray(4)

        data[0] = self._convert_brightness(config.max_level)
        data[1] = self._convert_brightness(config.min_level)
        data[2] = 0xFF
        data[3] = 0xFF

        return self._send_module_config_command(module_id, channel, Command.WRITE_STATE, broadcast, self._command_mode(module_mode), data, fmt=17, parser=BrightnessConfigurationParser())

    def bind(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.BIND, broadcast, self._command_mode(module_mode))

    def unbind(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        return self._send_module_base_command(module_id, channel, Command.UNBIND, broadcast, self._command_mode(module_mode))

    def set_service_mode(self, state: bool, module_id: int = None, channel: int = None, broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        data = bytearray(1)
        if state:
            data[0] = 1
        return self._send_module_base_command(module_id, channel, Command.SERVICE, broadcast, self._command_mode(module_mode), data)

    def add_listener(self, channel: int, listener: NooLiteFListener):
        listeners = self._listener_map.get(channel, [])
        listeners.append(listener)
        self._listener_map[channel] = listeners

    def remove_listener(self, channel: int, listener: NooLiteFListener):
        listeners = self._listener_map.get(channel, [])
        listeners.remove(listener)
        if len(listeners) == 0:
            listeners = None
        self._listener_map[channel] = listeners

    # Listeners
    def _on_receive(self, incoming_data: IncomingData):
        listeners = self._listener_map.get(incoming_data.channel, None)

        if listeners is None:
            return

        for listener in listeners:
            if listener is None:
                return

            if incoming_data.command == Command.ON:
                listener.on_on()
            elif incoming_data.command == Command.OFF:
                listener.on_off()
            elif incoming_data.command == Command.SWITCH:
                listener.on_switch()
            elif incoming_data.command == Command.TEMPORARY_ON:
                delay = None
                if incoming_data.format == 5:
                    delay = incoming_data.data[0]
                elif incoming_data.format == 6:
                    delay = incoming_data.data[0] + (incoming_data.data[1] << 15)
                listener.on_temporary_on(delay)
            elif incoming_data.command == Command.BRIGHT_UP:
                listener.on_brightness_tune(Direction.UP)
            elif incoming_data.command == Command.BRIGHT_DOWN:
                listener.on_brightness_tune(Direction.DOWN)
            elif incoming_data.command == Command.BRIGHT_BACK:
                listener.on_brightness_tune_back()
            elif incoming_data.command == Command.BRIGHT_STEP_UP:
                if incoming_data.format == 1:
                    step = incoming_data.data[0]
                else:
                    step = None
                listener.on_brightness_tune_step(Direction.UP, step)
            elif incoming_data.command == Command.BRIGHT_STEP_DOWN:
                if incoming_data.format == 1:
                    step = incoming_data.data[0]
                else:
                    step = None
                listener.on_brightness_tune_step(Direction.DOWN, step)
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
                        direction = Direction.UP
                    else:
                        direction = Direction.DOWN
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
            elif incoming_data.command == Command.BATTERY_LOW:
                listener.on_battery_low()
