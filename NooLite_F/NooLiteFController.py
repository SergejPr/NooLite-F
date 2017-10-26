
from abc import ABC, abstractmethod
from enum import IntEnum


class ModuleType(IntEnum):
    NOOLITE = 0
    NOOLITE_F = 1


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


class NooLiteFController(ABC):

    # Base power control
    @abstractmethod
    def off(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Turn off the modules

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Turn on the modules

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def temporary_on(self, channel: int, duration: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Turn on the modules for a specified time interval

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param duration: the time during which the modules will be turned on, duration measurement equals 5 sec.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def enable_temporary_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Enable "temporary on" mode

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def disable_temporary_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Disable "temporary on" mode

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch modules mode (on/off)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune(self, channel: int, direction: BrightnessDirection, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Start to increase/decrease brightness

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param direction: direction of the brightness changing
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_back(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Invert direction of the brightness change

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_stop(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Stop brightness changing

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_custom(self, channel: int, direction: BrightnessDirection, speed: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F):
        """ Start to increase/decrease brightness with a specified speed

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param direction: direction of the brightness changing
        :param speed: speed of the brightness changing. The range of value is 0 .. 1.0
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_step(self, channel: int, direction: BrightnessDirection, step: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F):
        """ Increase/decrease brightness once with a specified step

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param direction: direction of the brightness changing
        :param step: step in microseconds. If specify then can have values in range (1..255) or 0 (it is means 256), by default step equals 64
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_brightness(self, channel: int, brightness: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Set brightness

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param brightness: brightness level. The range of value is 0 .. 1.0
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def roll_rgb_color(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Start color changing (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_color(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch color (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_mode(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch color changing modes (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_mode_speed(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch speed of the color changing (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_rgb_brightness(self, channel: int, red: float, green: float, blue: float, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Set brightness for each rgb color (only for RGB Led modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param red: red color brightness level. The range of value is 0 .. 1.0
        :param green: green color brightness level. The range of value is 0 .. 1.0
        :param blue: blue color brightness level. The range of value is 0 .. 1.0
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def load_preset(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Load saved module state from preset

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def save_preset(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Save current module state as preset

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_state(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Read module state (only for NooLite-F modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def bind(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Send bind command to module

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def unbind(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Send unbind command to module

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def service_mode_on(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Turn on the service mode on module (only for NooLite-F modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def service_mode_off(self, channel: int, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Turn off the service mode on module (only for NooLite-F modules)

        :param channel: the number of the channel for command. The command will be send to all modules that are binded with selected channel.
        :param broadcast: broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass
