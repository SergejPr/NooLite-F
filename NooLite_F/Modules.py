from NooLite_F import NooLiteFController, ModuleType, ModuleInfo, BrightnessDirection


class Switch(object):

    _port: str
    _channel: int
    _module_type: ModuleType
    _broadcast_mode: bool
    _controller: NooLiteFController

    def __init__(self, controller: NooLiteFController, channel: int, module_type: ModuleType = ModuleType.NOOLITE_F, broadcast_mode: bool = False):
        self._channel = channel
        self._module_type = module_type
        self._broadcast_mode = broadcast_mode
        self._controller = controller

    def on(self) -> [(bool, ModuleInfo)]:
        return self._controller.on(self._channel, self._broadcast_mode, self._module_type)

    def off(self) -> [(bool, ModuleInfo)]:
        return self._controller.off(self._channel, self._broadcast_mode, self._module_type)

    def switch(self) -> [(bool, ModuleInfo)]:
        return self._controller.off(self._channel, self._broadcast_mode, self._module_type)

    def load_preset(self) -> [(bool, ModuleInfo)]:
        return self._controller.load_preset(self._channel, self._broadcast_mode, self._module_type)

    def save_preset(self) -> [(bool, ModuleInfo)]:
        return self._controller.save_preset(self._channel, self._broadcast_mode, self._module_type)

    def read_state(self) -> [(bool, ModuleInfo)]:
        return self._controller.read_state(self._channel, self._broadcast_mode, self._module_type)

    def bind(self) -> [(bool, ModuleInfo)]:
        return self._controller.bind(self._channel, self._broadcast_mode, self._module_type)

    def unbind(self) -> [(bool, ModuleInfo)]:
        return self._controller.bind(self._channel, self._broadcast_mode, self._module_type)

    def service_mode_on(self) -> [(bool, ModuleInfo)]:
        return self._controller.service_mode_on(self._channel, self._broadcast_mode, self._module_type)

    def service_mode_off(self) -> [(bool, ModuleInfo)]:
        return self._controller.service_mode_off(self._channel, self._broadcast_mode, self._module_type)


class ExtendedSwitch(Switch):

    def temporary_on(self, duration: int) -> [(bool, ModuleInfo)]:
        return self._controller.temporary_on(self._channel, duration, self._broadcast_mode, self._module_type)

    def enable_temporary_on(self) -> [(bool, ModuleInfo)]:
        return self._controller.enable_temporary_on(self._channel, self._broadcast_mode, self._module_type)

    def disable_temporary_on(self) -> [(bool, ModuleInfo)]:
        return self._controller.disable_temporary_on(self._channel, self._broadcast_mode, self._module_type)


class Dimmer(ExtendedSwitch):

    def brightness_tune(self, direction: BrightnessDirection) -> [(bool, ModuleInfo)]:
        return self._controller.brightness_tune(self._channel, direction, self._broadcast_mode, self._module_type)

    def brightness_tune_back(self) -> [(bool, ModuleInfo)]:
        return self._controller.brightness_tune_back(self._channel, self._broadcast_mode, self._module_type)

    def brightness_tune_stop(self) -> [(bool, ModuleInfo)]:
        return self._controller.brightness_tune_stop(self._channel, self._broadcast_mode, self._module_type)

    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float):
        return self._controller.brightness_tune_custom(self._channel, direction, speed, self._broadcast_mode, self._module_type)

    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None):
        return self._controller.brightness_tune_step(self._channel, direction, step, self._broadcast_mode, self._module_type)

    def set_brightness(self, brightness: float) -> [(bool, ModuleInfo)]:
        return self._controller.set_brightness(self._channel, brightness, self._broadcast_mode, self._module_type)


class RGBLed(Switch):

    def brightness_tune(self, direction: BrightnessDirection) -> [(bool, ModuleInfo)]:
        return self._controller.brightness_tune(self._channel, direction, self._broadcast_mode, self._module_type)

    def brightness_tune_back(self) -> [(bool, ModuleInfo)]:
        return self._controller.brightness_tune_back(self._channel, self._broadcast_mode, self._module_type)

    def brightness_tune_stop(self) -> [(bool, ModuleInfo)]:
        return self._controller.brightness_tune_stop(self._channel, self._broadcast_mode, self._module_type)

    def set_brightness(self, brightness: float) -> [(bool, ModuleInfo)]:
        return self._controller.set_brightness(self._channel, brightness, self._broadcast_mode, self._module_type)

    def roll_rgb_color(self) -> [(bool, ModuleInfo)]:
        return self._controller.roll_rgb_color(self._channel, self._broadcast_mode, self._module_type)

    def switch_rgb_color(self) -> [(bool, ModuleInfo)]:
        return self._controller.switch_rgb_color(self._channel, self._broadcast_mode, self._module_type)

    def switch_rgb_mode(self) -> [(bool, ModuleInfo)]:
        return self._controller.switch_rgb_mode(self._channel, self._broadcast_mode, self._module_type)

    def switch_rgb_mode_speed(self) -> [(bool, ModuleInfo)]:
        return self._controller.switch_rgb_mode_speed(self._channel, self._broadcast_mode, self._module_type)

    def set_rgb_brightness(self, red: float, green: float, blue: float) -> [(bool, ModuleInfo)]:
        return self._controller.set_rgb_brightness(self._channel, red, green, blue, self._broadcast_mode, self._module_type)
