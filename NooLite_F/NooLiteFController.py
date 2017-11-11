
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


class BatteryState(IntEnum):
    OK = 0,
    LOW = 1,


class ModuleInfo(object):
    state: ModuleState = None
    mode: ModuleMode = None
    brightness: float = None
    id: int = None
    firmware: int = None
    type: int = None

    def __repr__(self):
        return "<ModuleInfo (0x{0:x}), id: 0x{1:x}, type: {2}, firmware: {3}, state: {4}, brightness: {5}, mode: {6}>"\
            .format(id(self), self.id, self.type, self.firmware, self.state, self.brightness, self.mode)


class RemoteListener(ABC):

    def on(self):
        pass

    def off(self):
        pass

    def switch(self):
        pass

    def load_preset(self):
        pass

    def save_preset(self):
        pass

    def temporary_on(self, duration: int):
        pass

    def brightness_tune(self, direction: BrightnessDirection):
        pass

    def brightness_tune_back(self):
        pass

    def brightness_tune_stop(self):
        pass

    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float):
        pass

    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None):
        pass

    def set_brightness(self, brightness: float):
        pass

    def roll_rgb_color(self):
        pass

    def switch_rgb_color(self):
        pass

    def switch_rgb_mode(self):
        pass

    def switch_rgb_mode_speed(self):
        pass

    def set_rgb_brightness(self, red: float, green: float, blue: float):
        pass

    def on_temp_humi(self, temp: float, humi: int, battery: BatteryState, analog: float):
        pass


class NooLiteFController(ABC):

    # Base power control
    @abstractmethod
    def off(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Turn off the modules

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Turn on the modules

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def temporary_on(self, duration: int, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Turn on the modules for a specified time interval

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param duration: the time during which the modules will be turned on, duration measurement equals 5 sec.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def enable_temporary_on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Enable "temporary on" mode

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def disable_temporary_on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Disable "temporary on" mode

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch modules mode (on/off)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune(self, direction: BrightnessDirection, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Start to increase/decrease brightness

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param direction: direction of the brightness changing
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_back(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Invert direction of the brightness change

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_stop(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Stop brightness changing

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Start to increase/decrease brightness with a specified speed

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param direction: direction of the brightness changing
        :param speed: speed of the brightness changing. The range of value is 0 .. 1.0
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Increase/decrease brightness once with a specified step

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param direction: direction of the brightness changing
        :param step: step in microseconds. If specify then can have values in range (1..255) or 0 (it is means 256), by default step equals 64
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_brightness(self, brightness: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Set brightness

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param brightness: brightness level. The range of value is 0 .. 1.0
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def roll_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Start color changing (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch color (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_mode(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch color changing modes (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_mode_speed(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Switch speed of the color changing (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_rgb_brightness(self, red: float, green: float, blue: float, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Set brightness for each rgb color (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param red: red color brightness level. The range of value is 0 .. 1.0
        :param green: green color brightness level. The range of value is 0 .. 1.0
        :param blue: blue color brightness level. The range of value is 0 .. 1.0
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def load_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Load saved module state from preset

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def save_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """ Save current module state as preset

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_state(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Read module state (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def bind(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Send bind command to module

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def unbind(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Send unbind command to module

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def service_mode_on(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Turn on the service mode on module (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def service_mode_off(self, module_id: int = None, channel: int = None, broadcast: bool = False, module_type: ModuleType = ModuleType.NOOLITE_F) -> [(bool, ModuleInfo)]:
        """  Turn off the service mode on module (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_listener(self, channel: int, listener: RemoteListener):
        """ Set the remote controls listener

        :param channel: channel to which the listener will be assigned
        :param listener: listener
        """
        pass
