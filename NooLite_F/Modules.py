from enum import IntEnum

from NooLite_F.NooLiteService import NooLiteService, ModuleInfo, Mode, BrightnessDirection


class ModuleType(IntEnum):
    NOOLITE = 0
    NOOLITE_F = 1


class Switch(object):
    _port: str
    _channel: int
    _module_type: ModuleType
    _broadcast_mode: bool

    _adapter: NooLiteService

    _mode_map = {
        ModuleType.NOOLITE: Mode.TX,
        ModuleType.NOOLITE_F: Mode.TX_F,
    }

    def __init__(self, port: str, channel: int, module_type: ModuleType, broadcast_mode: bool = False):
        self._channel = channel
        self._module_type = module_type
        self._adapter = NooLiteService(port)
        self._broadcast_mode = broadcast_mode

    @property
    def _mode(self) -> Mode:
        return self._mode_map[self._module_type]

    def on(self) -> [(bool, ModuleInfo)]:
        return self._adapter.on(self._channel, self._broadcast_mode, self._mode)

    def off(self) -> [(bool, ModuleInfo)]:
        return self._adapter.off(self._channel, self._broadcast_mode, self._mode)

    def switch(self) -> [(bool, ModuleInfo)]:
        return self._adapter.off(self._channel, self._broadcast_mode, self._mode)

    def temporary_on(self, duration: int) -> [(bool, ModuleInfo)]:
        return self._adapter.temporary_on(self._channel, duration, self._broadcast_mode, self._mode)

    def enable_temporary_on(self) -> [(bool, ModuleInfo)]:
        return self._adapter.enable_temporary_on(self._channel, self._broadcast_mode, self._mode)

    def disable_temporary_on(self) -> [(bool, ModuleInfo)]:
        return self._adapter.disable_temporary_on(self._channel, self._broadcast_mode, self._mode)

    def load_preset(self) -> [(bool, ModuleInfo)]:
        return self._adapter.load_preset(self._channel, self._broadcast_mode, self._mode)

    def save_preset(self) -> [(bool, ModuleInfo)]:
        return self._adapter.save_preset(self._channel, self._broadcast_mode, self._mode)

    def read_state(self) -> [(bool, ModuleInfo)]:
        return self._adapter.read_state(self._channel, self._broadcast_mode, self._mode)

    def bind(self) -> [(bool, ModuleInfo)]:
        return self._adapter.bind(self._channel, self._broadcast_mode, self._mode)

    def unbind(self) -> [(bool, ModuleInfo)]:
        return self._adapter.bind(self._channel, self._broadcast_mode, self._mode)

    def service_mode_on(self) -> [(bool, ModuleInfo)]:
        return self._adapter.service_mode_on(self._channel, self._broadcast_mode, self._mode)

    def service_mode_off(self) -> [(bool, ModuleInfo)]:
        return self._adapter.service_mode_off(self._channel, self._broadcast_mode, self._mode)


class Dimmer(Switch):

    def brightness_tune(self, direction: BrightnessDirection) -> [(bool, ModuleInfo)]:
        return self._adapter.brightness_tune(self._channel, direction, self._broadcast_mode, self._mode)

    def brightness_tune_back(self) -> [(bool, ModuleInfo)]:
        return self._adapter.brightness_tune_back(self._channel, self._broadcast_mode, self._mode)

    def brightness_tune_stop(self) -> [(bool, ModuleInfo)]:
        return self._adapter.brightness_tune_stop(self._channel, self._broadcast_mode, self._mode)

    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float):
        return self._adapter.brightness_tune_custom(self._channel, direction, speed, self._broadcast_mode, self._mode)

    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None):
        return self._adapter.brightness_tune_step(self._channel, direction, step, self._broadcast_mode, self._mode)

    def set_brightness(self, brightness: float) -> [(bool, ModuleInfo)]:
        return self._adapter.set_brightness(self._channel, brightness, self._broadcast_mode, self._mode)


class RGBLed(Dimmer):

    def roll_rgb_color(self) -> [(bool, ModuleInfo)]:
        return self._adapter.roll_rgb_color(self._channel, self._broadcast_mode, self._mode)

    def switch_rgb_color(self) -> [(bool, ModuleInfo)]:
        return self._adapter.switch_rgb_color(self._channel, self._broadcast_mode, self._mode)

    def switch_rgb_mode(self) -> [(bool, ModuleInfo)]:
        return self._adapter.switch_rgb_mode(self._channel, self._broadcast_mode, self._mode)

    def switch_rgb_mode_speed(self) -> [(bool, ModuleInfo)]:
        return self._adapter.switch_rgb_mode_speed(self._channel, self._broadcast_mode, self._mode)

    def set_rgb_brightness(self, red: float, green: float, blue: float) -> [(bool, ModuleInfo)]:
        return self._adapter.set_rgb_brightness(self._channel, red, green, blue, self._broadcast_mode, self._mode)
