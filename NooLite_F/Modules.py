from NooLite_F import NooLiteFController, ModuleMode, BrightnessDirection, ModuleConfig, DimmerCorrectionConfig
from NooLite_F import ResponseBaseInfo, ResponseExtraInfo, ResponseChannelsInfo, ResponseModuleConfig, ResponseDimmerCorrectionConfig


class Switch(object):

    def __init__(self, controller: NooLiteFController, module_id: int = None, channel: int = None, module_mode: ModuleMode = ModuleMode.NOOLITE_F, broadcast_mode: bool = False):
        self._channel = channel
        self._module_mode = module_mode
        self._broadcast_mode = broadcast_mode
        self._controller = controller
        self._module_id = module_id

    def on(self) -> [ResponseBaseInfo]:
        return self._controller.on(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def off(self) -> [ResponseBaseInfo]:
        return self._controller.off(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def switch(self) -> [ResponseBaseInfo]:
        return self._controller.switch(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def load_preset(self) -> [ResponseBaseInfo]:
        return self._controller.load_preset(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def save_preset(self) -> [ResponseBaseInfo]:
        return self._controller.save_preset(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def read_state(self) -> [ResponseBaseInfo]:
        return self._controller.read_state(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def read_extra_state(self) -> [ResponseExtraInfo]:
        return self._controller.read_extra_state(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def read_channels_state(self) -> [ResponseChannelsInfo]:
        return self._controller.read_channels_state(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def bind(self) -> [ResponseBaseInfo]:
        return self._controller.bind(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def unbind(self) -> [ResponseBaseInfo]:
        return self._controller.unbind(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def set_service_mode(self, state: bool) -> [ResponseBaseInfo]:
        return self._controller.set_service_mode(state, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def read_config(self) -> [ResponseModuleConfig]:
        return self._controller.read_module_config(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def write_config(self, config: ModuleConfig) -> [ResponseModuleConfig]:
        return self._controller.write_module_config(config, self._module_id, self._channel, self._broadcast_mode, self._module_mode)


class ExtendedSwitch(Switch):

    def temporary_on(self, duration: int) -> [ResponseBaseInfo]:
        return self._controller.temporary_on(duration, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def set_temporary_on_mode(self, enabled: bool) -> [ResponseBaseInfo]:
        return self._controller.set_temporary_on_mode(enabled, self._module_id, self._channel, self._broadcast_mode, self._module_mode)


class Dimmer(ExtendedSwitch):

    def brightness_tune(self, direction: BrightnessDirection) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune(direction, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def brightness_tune_back(self) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune_back(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def brightness_tune_stop(self) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune_stop(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune_custom(direction, speed, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune_step(direction, step, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def set_brightness(self, brightness: float) -> [ResponseBaseInfo]:
        return self._controller.set_brightness(brightness, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def read_dimmer_correction(self) -> [ResponseDimmerCorrectionConfig]:
        return self._controller.read_dimmer_correction(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def write_dimmer_correction(self, config: DimmerCorrectionConfig) -> [ResponseDimmerCorrectionConfig]:
        return self._controller.write_dimmer_correction(config, self._module_id, self._channel, self._broadcast_mode, self._module_mode)


class Fan(ExtendedSwitch):

    def speed_tune(self, direction: BrightnessDirection) -> [ResponseBaseInfo]:
        return self._controller.speed_tune(direction, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def speed_tune_back(self) -> [ResponseBaseInfo]:
        return self._controller.speed_tune_back(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def speed_tune_stop(self) -> [ResponseBaseInfo]:
        return self._controller.speed_tune_stop(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def speed_tune_custom(self, direction: BrightnessDirection, speed: float) -> [ResponseBaseInfo]:
        return self._controller.speed_tune_custom(direction, speed, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def speed_tune_step(self, direction: BrightnessDirection, step: int = None) -> [ResponseBaseInfo]:
        return self._controller.speed_tune_step(direction, step, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def set_speed(self, brightness: float) -> [ResponseBaseInfo]:
        return self._controller.set_speed(brightness, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def read_dimmer_correction(self) -> [ResponseDimmerCorrectionConfig]:
        return self._controller.read_dimmer_correction(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def write_dimmer_correction(self, config: DimmerCorrectionConfig) -> [ResponseDimmerCorrectionConfig]:
        return self._controller.write_dimmer_correction(config, self._module_id, self._channel, self._broadcast_mode, self._module_mode)


class RGBLed(Switch):

    def brightness_tune(self, direction: BrightnessDirection) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune(direction, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def brightness_tune_back(self) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune_back(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def brightness_tune_stop(self) -> [ResponseBaseInfo]:
        return self._controller.brightness_tune_stop(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def set_brightness(self, brightness: float) -> [ResponseBaseInfo]:
        return self._controller.set_brightness(brightness, self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def roll_rgb_color(self) -> [ResponseBaseInfo]:
        return self._controller.roll_rgb_color(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def switch_rgb_color(self) -> [ResponseBaseInfo]:
        return self._controller.switch_rgb_color(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def switch_rgb_mode(self) -> [ResponseBaseInfo]:
        return self._controller.switch_rgb_mode(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def switch_rgb_mode_speed(self) -> [ResponseBaseInfo]:
        return self._controller.switch_rgb_mode_speed(self._module_id, self._channel, self._broadcast_mode, self._module_mode)

    def set_rgb_brightness(self, red: float, green: float, blue: float) -> [ResponseBaseInfo]:
        return self._controller.set_rgb_brightness(red, green, blue, self._module_id, self._channel, self._broadcast_mode, self._module_mode)
