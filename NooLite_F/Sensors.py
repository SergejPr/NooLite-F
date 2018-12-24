from NooLite_F import NooLiteFController, RemoteControllerListener, BatteryState, Direction


class Sensor(RemoteControllerListener):

    def __init__(self, controller: NooLiteFController, channel: int, on_battery_low=None):
        self._controller = controller
        self._channel = channel
        self._battery_low_listener = on_battery_low
        self._controller.add_listener(channel, self)

    def release(self):
        self._controller.remove_listener(self._channel, self)
        self._controller = None

    def on_battery_low(self):
        if self._battery_low_listener is not None:
            self._battery_low_listener()


class TempHumiSensor(Sensor):

    def __init__(self, controller: NooLiteFController, channel: int, on_data):
        super().__init__(controller, channel)
        self._on_data_listener = on_data

    def on_temp_humi(self, temp: float, humi: int, battery: BatteryState, analog: float):
        if self._on_data_listener is not None:
            self._on_data_listener(temp, humi, analog, battery)


class MotionSensor(Sensor):

    def __init__(self, controller: NooLiteFController, channel: int, on_motion, on_battery_low=None):
        super().__init__(controller, channel, on_battery_low)
        self._motion_listener = on_motion

    def on_temporary_on(self, duration: int):
        if self._motion_listener is not None:
            self._motion_listener(duration)


class BinarySensor(Sensor):
    def __init__(self, controller: NooLiteFController, channel: int, on_on=None, on_off=None, on_battery_low=None):

        super().__init__(controller, channel, on_battery_low)
        self._on_listener = on_on
        self._off_listener = on_off

    def on_on(self):
        if self._on_listener is not None:
            self._on_listener()

    def on_off(self):
        if self._off_listener is not None:
            self._off_listener()


class RemoteController(Sensor):
    def __init__(self, controller: NooLiteFController, channel: int,
                 on_on=None, on_off=None, on_switch=None,
                 on_tune_start=None, on_tune_back=None, on_tune_stop=None,
                 on_load_preset=None, on_save_preset=None, on_battery_low=None):

        super().__init__(controller, channel, on_battery_low)
        self._on_listener = on_on
        self._off_listener = on_off
        self._switch_listener = on_switch
        self._tune_listener = on_tune_start
        self._back_listener = on_tune_back
        self._stop_listener = on_tune_stop
        self._load_preset_listener = on_load_preset
        self._save_preset_listener = on_save_preset

    def on_on(self):
        if self._on_listener is not None:
            self._on_listener()

    def on_off(self):
        if self._off_listener is not None:
            self._off_listener()

    def on_switch(self):
        if self._switch_listener is not None:
            self._switch_listener()

    def on_load_preset(self):
        if self._load_preset_listener is not None:
            self._load_preset_listener()

    def on_save_preset(self):
        if self._save_preset_listener is not None:
            self._save_preset_listener()

    def on_brightness_tune(self, direction: Direction):
        if self._tune_listener is not None:
            self._tune_listener(direction)

    def on_brightness_tune_stop(self):
        if self._stop_listener is not None:
            self._stop_listener()

    def on_brightness_tune_back(self):
        if self._back_listener is not None:
            self._back_listener()


class RGBRemoteController(Sensor):
    def __init__(self, controller: NooLiteFController, channel: int,
                 on_switch=None, on_tune_back=None, on_tune_stop=None,
                 on_roll_color=None, on_switch_color=None, on_switch_mode=None, on_switch_speed=None, on_battery_low=None):

        super().__init__(controller, channel, on_battery_low)
        self._switch_listener = on_switch
        self._back_listener = on_tune_back
        self._stop_listener = on_tune_stop
        self._roll_color_listener = on_roll_color
        self._switch_color_listener = on_switch_color
        self._switch_mode_listener = on_switch_mode
        self._switch_speed_listener = on_switch_speed

    def on_switch(self):
        if self._switch_listener is not None:
            self._switch_listener()

    def on_brightness_tune_stop(self):
        if self._stop_listener is not None:
            self._stop_listener()

    def on_brightness_tune_back(self):
        if self._back_listener is not None:
            self._back_listener()

    def on_switch_rgb_color(self):
        if self._switch_color_listener is not None:
            self._switch_color_listener()

    def on_roll_rgb_color(self):
        if self._roll_color_listener is not None:
            self._roll_color_listener()

    def on_switch_rgb_mode(self):
        if self._switch_mode_listener is not None:
            self._switch_mode_listener()

    def on_switch_rgb_mode_speed(self):
        if self._switch_speed_listener is not None:
            self._switch_speed_listener()
