
from enum import IntEnum
from NooLite_F.Adapter import Adapter, Response, Request, Command, Mode, ResponseCode, Action


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


# TODO: replace format with enum or constants???
class NooLiteF(object):

    adapter = None

    def __init__(self, port: str):
        self.adapter = Adapter(port)

    def off(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Turn off the modules

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.OFF, broadcast, mode)
        return self.handle_command_responses(responses)

    def on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Turn on the modules

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.ON, broadcast, mode)
        return self.handle_command_responses(responses)

    # duration measurement equals 5 sec.
    def temporary_on(self, channel: int, duration: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Turn on the modules for a specified time interval

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param duration: the time during which the modules will be turned on
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        data: bytearray = bytearray(2)
        data[0] = duration & 0x00FF
        data[1] = duration & 0xFF00

        responses = self.send_module_command(channel, Command.TEMPORARY_ON, broadcast, mode, data, 6)
        return self.handle_command_responses(responses)

    def enable_temporary_on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Enable "temporary on" mode

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        data: bytearray = bytearray(1)
        data[0] = 0

        responses = self.send_module_command(channel, Command.MODES, broadcast, mode, data, 1)
        return self.handle_command_responses(responses)

    def disable_temporary_on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Disable "temporary on" mode

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        data: bytearray = bytearray(1)
        data[0] = 1

        responses = self.send_module_command(channel, Command.MODES, broadcast, mode, data, 1)
        return self.handle_command_responses(responses)

    def switch(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Switch modules mode (on/off)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.SWITCH, broadcast, mode)
        return self.handle_command_responses(responses)

    def bright_tune(self, channel: int, direction: BrightnessDirection, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Start to increase/decrease brightness

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param direction: direction of the brightness changing
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        if direction == BrightnessDirection.UP:
            command = Command.BRIGHT_UP
        else:
            command = Command.BRIGHT_DOWN

        responses = self.send_module_command(channel, command, broadcast, mode)
        return self.handle_command_responses(responses)

    def bright_tune_back(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Invert direction of the brightness change

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.BRIGHT_BACK, broadcast, mode)
        return self.handle_command_responses(responses)

    def bright_tune_stop(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Stop brightness changing

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.STOP_BRIGHT, broadcast, mode)
        return self.handle_command_responses(responses)

    # speed in range from (0 .. 1.0)
    def bright_tune_custom(self, channel: int, direction: BrightnessDirection, speed: float, broadcast: bool = False, mode: Mode = Mode.TX_F):
        """ Start to increase/decrease brightness with a specified speed

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param direction: direction of the brightness changing
        :param speed: speed of the brightness changing. The range of value is 0 .. 1.0
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """

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

    def bright_step(self, channel: int, direction: BrightnessDirection, step: int = None, broadcast: bool = False, mode: Mode = Mode.TX_F):
        """ Increase/decrease brightness once with a specified step

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param direction: direction of the brightness changing
        :param step: step in microseconds. If specify then can have values in range (1..255) or 0 (it is means 256), by default step equals 64
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
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

    def set_brightness(self, channel: int, bright: float, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Set brightness

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param bright: brightness level. The range of value is 0 .. 1.0
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
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
        """ Start color changing (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.ROLL_COLOR, broadcast, mode)
        return self.handle_command_responses(responses)

    def switch_rgb_color(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Switch color (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.SWITCH_COLOR, broadcast, mode)
        return self.handle_command_responses(responses)

    def switch_rgb_mode(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Switch color changing modes (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.SWITCH_MODE, broadcast, mode)
        return self.handle_command_responses(responses)

    def switch_rgb_mode_speed(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Switch speed of the color changing (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.SPEED_MODE, broadcast, mode)
        return self.handle_command_responses(responses)

    # brightness value is float value in range 0 .. 1.0
    def set_rgb_brightness(self, channel: int, red: float, green: float, blue: float, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Set brightness for each rgb color (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param red: red color brightness level. The range of value is 0 .. 1.0
        :param green: green color brightness level. The range of value is 0 .. 1.0
        :param blue: blue color brightness level. The range of value is 0 .. 1.0
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        data: bytearray = bytearray(3)
        data[0] = self.convert_color_brightness(red)
        data[1] = self.convert_color_brightness(green)
        data[2] = self.convert_color_brightness(blue)

        responses = self.send_module_command(channel, Command.SET_BRIGHTNESS, broadcast, mode, data, 3)
        return self.handle_command_responses(responses)

    def load_preset(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Load saved module state from preset

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.LOAD_PRESET, broadcast, mode)
        return self.handle_command_responses(responses)

    def save_preset(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """ Save current module state as preset

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.SAVE_PRESET, broadcast, mode)
        return self.handle_command_responses(responses)

    def read_state(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """  Read module state (only for NooLite-F modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.READ_STATE, broadcast, mode)
        return self.handle_command_responses(responses)

    def bind(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """  Send bind command to module

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.BIND, broadcast, mode)
        return self.handle_command_responses(responses)

    def unbind(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """  Send unbind command to module

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        responses = self.send_module_command(channel, Command.UNBIND, broadcast, mode)
        return self.handle_command_responses(responses)

    def service_mode_on(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """  Turn on the service mode on module (only for NooLite-F modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        data: bytearray = bytearray(1)
        data[0] = 1

        responses = self.send_module_command(channel, Command.SERVICE, broadcast, mode, data)
        return self.handle_command_responses(responses)

    def service_mode_off(self, channel: int, broadcast: bool = False, mode: Mode = Mode.TX_F) -> [(bool, ModuleInfo)]:
        """  Turn off the service mode on module (only for NooLite-F modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param mode: mode of the command sending. TX - for nooLite module (without feedback), TX_F - for noolite-F modules (with feedback).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
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

    def convert_color_brightness(self, bright: float) -> int:
        if bright >= 1:
            value = 255
        elif bright <= 0:
            value = 0
        else:
            value = int(255 * bright)

        return value
