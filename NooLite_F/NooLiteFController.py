from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, List


class ModuleMode(Enum):
    NOOLITE = 0
    NOOLITE_F = 1


class ModuleState(Enum):
    OFF = 1
    ON = 2
    TEMPORARY_ON = 3


class NooliteModeState(Enum):
    DISABLED = 0
    TEMPORARY_DISABLED = 2
    ENABLED = 3


class ServiceModeState(Enum):
    BIND_OFF = 0
    BIND_ON = 1


class Direction(Enum):
    UP = 0
    DOWN = 1


class BatteryState(Enum):
    OK = 0
    LOW = 1


class InputMode(Enum):
    DISABLED = 0
    SWITCH = 1
    BUTTON = 2
    BREAKER = 3


class ModuleConfig(object):
    dimmer_mode = None
    input_mode = None
    save_state_mode = None
    init_state = None
    noolite_support = None
    noolite_retranslation = None

    def __repr__(self):
        return "<ModuleConfiguration (0x{0:x}), save state: {1}, dimer mode: {2}, noolite support: {3}, extra input mode: {4}, init state: {5}, retranslate noolite: {6}>" \
            .format(id(self), self.save_state_mode, self.dimmer_mode, self.noolite_support, self.input_mode,
                    self.init_state, self.noolite_retranslation)


class DimmerCorrectionConfig(object):
    min_level = 0.0
    max_level = 1.0

    def __repr__(self):
        return "<BrightnessConfiguration (0x{0:x}), min level: {1}, max_level: {2}>" \
            .format(id(self), self.min_level, self.max_level)


class ModuleInfo(object):
    id = None
    firmware = None
    type = None

    def __repr__(self):
        return "<ModuleInfo (0x{0:x}), id: 0x{1:x}, type: {2}, firmware: {3}>" \
            .format(id(self), self.id, self.type, self.firmware)


class ModuleBaseStateInfo(object):
    state = None
    service_mode = None
    brightness = None

    def __repr__(self):
        return "<ModuleBaseStateInfo (0x{0:x}), state: {1}, brightness: {2}, service mode: {3}>" \
            .format(id(self), self.state, self.brightness, self.service_mode)


class ModuleExtraStateInfo(object):
    extra_input_state = None
    noolite_mode_state = None

    def __repr__(self):
        return "<ModuleExtraStateInfo (0x{0:x}), button state: {1}, noolite mode state: {2}>" \
            .format(id(self), self.extra_input_state, self.noolite_mode_state)


class ModuleChannelsStateInfo(object):
    noolite_cells = None
    noolite_f_cells = None

    def __repr__(self):
        return "<ModuleCellsStateInfo (0x{0:x}), noolite channels: {1}, noolite-f channels: {2}>" \
            .format(id(self), self.noolite_cells, self.noolite_f_cells)


ResponseBaseInfo = Tuple[bool, ModuleInfo, ModuleBaseStateInfo]
ResponseExtraInfo = Tuple[bool, ModuleInfo, ModuleExtraStateInfo]
ResponseChannelsInfo = Tuple[bool, ModuleInfo, ModuleChannelsStateInfo]
ResponseModuleConfig = Tuple[bool, ModuleConfig]
ResponseDimmerCorrectionConfig = Tuple[bool, DimmerCorrectionConfig]


class NooLiteFListener(ABC):

    def on_on(self):
        pass

    def on_off(self):
        pass

    def on_switch(self):
        pass

    def on_load_preset(self):
        pass

    def on_save_preset(self):
        pass

    def on_temporary_on(self, duration: int):
        pass

    def on_brightness_tune(self, direction: Direction):
        pass

    def on_brightness_tune_back(self):
        pass

    def on_brightness_tune_stop(self):
        pass

    def on_brightness_tune_custom(self, direction: Direction, speed: float):
        pass

    def on_brightness_tune_step(self, direction: Direction, step: int = None):
        pass

    def on_set_brightness(self, brightness: float):
        pass

    def on_roll_rgb_color(self):
        pass

    def on_switch_rgb_color(self):
        pass

    def on_switch_rgb_mode(self):
        pass

    def on_switch_rgb_mode_speed(self):
        pass

    def on_set_rgb_brightness(self, red: float, green: float, blue: float):
        pass

    def on_temp_humi(self, temp: float, humi: int, battery: BatteryState, analog: float):
        pass

    def on_battery_low(self):
        pass


class NooLiteFController(ABC):

    # Base power control
    @abstractmethod
    def off(self, module_id: int = None, channel: int = None, broadcast: bool = False,
            module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Turn off the modules

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def on(self, module_id: int = None, channel: int = None, broadcast: bool = False,
           module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Turn on the modules

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def temporary_on(self, duration: int, module_id: int = None, channel: int = None, broadcast: bool = False,
                     module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Turn on the modules for a specified time interval

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param duration: the time during which the modules will be turned on, duration measurement equals 5 sec.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_temporary_on_mode(self, enabled: bool, module_id: int = None, channel: int = None, broadcast: bool = False,
                              module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Enable/disable "temporary on" mode

        :param enabled: new "temporary on" mode state (enable/disable).
        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch(self, module_id: int = None, channel: int = None, broadcast: bool = False,
               module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Switch modules mode (on/off)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune(self, direction: Direction, module_id: int = None, channel: int = None,
                        broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[
        ResponseBaseInfo]:
        """ Start to increase/decrease brightness

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param direction: direction of the brightness changing
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_back(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                             module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Invert direction of the brightness change

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_stop(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                             module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Stop brightness changing

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_custom(self, direction: Direction, speed: float, module_id: int = None,
                               channel: int = None, broadcast: bool = False,
                               module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Start to increase/decrease brightness with a specified speed

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param direction: direction of the brightness changing
        :param speed: speed of the brightness changing. The range of value is 0 .. 1.0
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def brightness_tune_step(self, direction: Direction, step: int = None, module_id: int = None,
                             channel: int = None, broadcast: bool = False,
                             module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Increase/decrease brightness once with a specified step

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param direction: direction of the brightness changing
        :param step: step in microseconds. If specify then can have values in range (1..255) or 0 (it is means 256), by default step equals 64
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_brightness(self, brightness: float, module_id: int = None, channel: int = None, broadcast: bool = False,
                       module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Set brightness

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param brightness: brightness level. The range of value is 0 .. 1.0
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def roll_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                       module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Start color changing (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_color(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                         module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Switch color (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_mode(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                        module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Switch color changing modes (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def switch_rgb_mode_speed(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                              module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Switch speed of the color changing (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_rgb_brightness(self, red: float, green: float, blue: float, module_id: int = None, channel: int = None,
                           broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[
        ResponseBaseInfo]:
        """ Set brightness for each rgb color (only for RGB Led modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param red: red color brightness level. The range of value is 0 .. 1.0
        :param green: green color brightness level. The range of value is 0 .. 1.0
        :param blue: blue color brightness level. The range of value is 0 .. 1.0
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def load_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                    module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Load saved module state from preset

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def save_preset(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                    module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """ Save current module state as preset

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_state(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                   module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """  Read module base state (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_extra_state(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                         module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseExtraInfo]:
        """  Read module extra state: extra input state, noolite mode state (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module extra info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_channels_state(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                            module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseChannelsInfo]:
        """  Read module available cells count for binding (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module cells count for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_module_config(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                           module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseModuleConfig]:
        """  Read module configuration (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module configuration for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def write_module_config(self, config: ModuleConfig, module_id: int = None, channel: int = None,
                            broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[
        ResponseModuleConfig]:
        """  Write module configuration (only for NooLite-F modules)

        :param config: the module configuration. If parameter in configuration has value None, then it won't changed.
        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and new module configuration for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def read_dimmer_correction(self, module_id: int = None, channel: int = None, broadcast: bool = False,
                               module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseDimmerCorrectionConfig]:
        """  Read dimmer correction values. Affects only on power modules in dimmer mode (only for NooLite-F modules)

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and dimmer configuration for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def write_dimmer_correction(self, config: DimmerCorrectionConfig, module_id: int = None, channel: int = None,
                                broadcast: bool = False, module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[
        ResponseDimmerCorrectionConfig]:
        """  Writes dimmer correction values. Affects only on power modules in dimmer mode (only for NooLite-F modules)

        :param config: new dimmer correction for dimmer mode.
        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and new brightness configuration for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def bind(self, module_id: int = None, channel: int = None, broadcast: bool = False,
             module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """  Send bind command to module

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def unbind(self, module_id: int = None, channel: int = None, broadcast: bool = False,
               module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """  Send unbind command to module

        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def set_service_mode(self, state: bool, module_id: int = None, channel: int = None, broadcast: bool = False,
                         module_mode: ModuleMode = ModuleMode.NOOLITE_F) -> List[ResponseBaseInfo]:
        """  Turn on/off the service mode on module (only for NooLite-F modules)

        :param state: new service mode state (on/off).
        :param module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
        :param channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
        :param broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
        :param module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).
        :return: for nooLite-F command returns array which contains command result and module info for each module that are binded with selected channel. For nooLite modules returns nothing.
        """
        pass

    @abstractmethod
    def add_listener(self, channel: int, listener: NooLiteFListener):
        """ Add the remote controls listener to channel.

        :param channel: channel to which the listener will be assigned
        :param listener: listener
        """
        pass

    @abstractmethod
    def remove_listener(self, channel: int, listener: NooLiteFListener):
        """ Remove the remote controls listener from channel.

        :param channel: channel to which the listener will be assigned
        :param listener: listener
        """
        pass
