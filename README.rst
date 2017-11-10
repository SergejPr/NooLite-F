NooLite-F
=========

Send commands to modules
========================

Python module to work with NooLite-F (MTRF-64-USB)
There are possible three levels of usage:

Low level of usage.
-------------------
You can work directly with adapter::

    adapter = MTRF64USBAdapter("COM3")

    request = Request()
    request.action = Action.SEND_COMMAND
    request.mode = Mode.TX
    request.channel = 60
    request.command = Command.TEMPORARY_ON
    request.format = 6
    request.data[0] = 1

    response = adapter.send(request)

    print(response)

    request = Request()
    request.action = Action.SEND_COMMAND_TO_ID
    request.mode = Mode.TX_F
    request.id = 0x5023
    request.command = Command.SWITCH

    response = adapter.send(request)

    print(response)


**Note** Request and response directly maps to low-level api for adapter.
You can find more details about MTRF-64-USB api on official NooLite site: https://www.noo.com.by/

Middle level of usage.
----------------------
You can use MTRF64Controller and abstract from manual request data creating. Just call appropriate function::

    controller = MTRF64Controller("COM3")
    controller.set_brightness(channel=60, brightness=0.3, module_type=ModuleType.NOOLITE)

    controller.switch(module_id=0x5435, module_type=ModuleType.NOOLITE-F)


Controller supports following commands:

* on - turn on the module
* off - turn off the module
* switch - switch module state

* temporary_on - turn on the module for a specified time
* enable_temporary_on - enable "temporary on" mode
* disable_temporary_on - disable "temporary on" mode

* bright_tune - start to increase/decrease brightness
* bright_tune_back - invert direction of the brightness change
* bright_tune_stop - stop brightness changing
* bright_tune_custom - start to increase/decrease brightness with a specified speed
* bright_step - increase/decrease brightness once with a specified step
* set_brightness - set brightness

* load_preset - load saved module state from preset
* save_preset - save current module state as preset

* roll_rgb_color - start color changing **(only for RGB Led modules)**
* switch_rgb_color - switch color  **(only for RGB Led modules)**
* switch_rgb_mode - switch color changing modes **(only for RGB Led modules)**
* switch_rgb_mode_speed - switch speed of the color changing **(only for RGB Led modules)**
* set_rgb_brightness - set brightness for each rgb color **(only for RGB Led modules)**

* read_state - read module state **(only for NooLite-F modules)**

* bind - send bind command to module
* unbind - send unbind command to module
* service_mode_on - turn on the service mode on module **(only for NooLite-F modules)**
* service_mode_off - turn off the service mode on module **(only for NooLite-F modules)**

Each command can accept following parameters:

- module_id: the module id. The command will be send to module with specified id (used only for NOOLITE-F modules).
- channel: the number of the channel. The command will be send to all modules that are binded with selected channel. If module_id is also specified then command will be send only to appropriate device in channel.
- broadcast: broadcast mode. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False). If module_id is specified or mode is NOOLITE then broadcast parameter will be ignored.
- module_type: type of the module, used to determine adapter mode for send command (default - NOOLITE_F).

Some commands require additional parameters. For more details see inline help.


In response for each command returns:

* for **nooLite-F** modules returns array which contains command result and module info for each module that are binded with selected channel.
* for **nooLite** modules returns nothing.

Command result equals True if command send successfully, otherwise False.
Module info contains information about module: type, firmware version, state (on/off/temporary on), current brightness and bind mode (on/off)::

    [
        (True, <ModuleInfo (0x2e25b90), id: 0x52e9, type: 1, hardware: 3, state: 1, brightness: 1.0, mode: 0>),
        (True, <ModuleInfo (0x2e25a90), id: 0x52e3, type: 1, hardware: 3, state: 1, brightness: 1.0, mode: 0>)
    ]

If command result is False, then module info is None.::

    [(False, None)]


High level of usage.
--------------------
You can use special classes that are wrappers around controller. Each class is representation of the
concrete module or modules assigned with specific channel::

    controller = MTRF64Controller("COM3")
    dimmer = Dimmer(controller, 62, ModuleType.NOOLITE)
    dimmer.set_brightness(0.4)

    switch = Switch(controller, channel=60, ModuleType.NOOLITE)
    switch.on()

    switch = Switch(controller, module_id=0x5023, ModuleType.NOOLITE_F)
    switch.switch()


Receiving commands from remote controls
=======================================

You can use two ways to read commands from remote controls.

Using adapter.
--------------

You can read command from remote controls using MTRF64USBAdapter directly. All received commands are stored in internal queue.
You can get stored commands by call get method::

    adapter = MTRF64USBAdapter("COM3")

    response = adapter.get()

    print(response)



Using listener.
---------------

Also you can create special listener and set it to controller::

    controller = MTRF64Controller("COM3")
    switch = RGBLed(controller, channel=62, ModuleType.NOOLITE)


    class Listener(RemoteListener):
        def off(self):
            switch.off()

        def roll_rgb_color(self):
            switch.roll_rgb_color()

        def brightness_tune_stop(self):
            switch.brightness_tune_stop()

        def on(self):
            switch.on()

        def temporary_on(self, duration: int):
            pass

        def set_brightness(self, brightness: float):
            switch.set_brightness(brightness)

        def brightness_tune_step(self, direction: BrightnessDirection, step: int = None):
            pass

        def brightness_tune_custom(self, direction: BrightnessDirection, speed: float):
            pass

        def brightness_tune_back(self):
            switch.brightness_tune_back()

        def save_preset(self):
            switch.save_preset()

        def brightness_tune(self, direction: BrightnessDirection):
            switch.brightness_tune(direction)

        def switch_rgb_mode_speed(self):
            switch.switch_rgb_mode_speed()

        def switch_rgb_mode(self):
            switch.switch_rgb_mode()

        def switch(self):
            switch.switch()

        def switch_rgb_color(self):
            switch.switch_rgb_color()

        def load_preset(self):
            switch.load_preset()

        def set_rgb_brightness(self, red: float, green: float, blue: float):
            switch.set_rgb_brightness(red, green, blue)


    listener = Listener()
    controller.set_listener(63, listener)


Note
====

Tested with MTRF-64-USB adapter and SLF-1-300 (NooLite-F), SD-1-180 (NooLite), SU-1-500 (NooLite) modules.
