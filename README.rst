NooLite-F
=========

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

    adapter.open()

    response = adapter.send_request(request)

    adapter.close()

    print(response)

**Note** Request and response directly maps to low-level api for adapter.
You can find more details about MTRF-64-USB api on official NooLite site: https://www.noo.com.by/

Middle level of usage.
----------------------
You can use MTRF64Controller and abstract from manual request data creating. Just call appropriate function::

    controller = MTRF64Controller("COM3")
    controller.set_brightness(channel=60, brightness=0.3, module_type=ModuleType.NOOLITE)


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

* channel - the number of the channel for command. The command will be send to all modules that are binded with selected channel.
* broadcast - broadcast mode for command. If True then command will be send simultaneously to all modules that are binded with selected channel (default - False)
* module_type - type of module assigned to the specified channel. It is need to determine correct adapter mode for command sending. **Note:** NooLite-F can accept commands sending in NooLite mode.

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

    switch = Switch(controller, 60, ModuleType.NOOLITE)
    switch.on()



Note
====

Tested with MTRF-64-USB adapter and SLF-1-300 (NooLite-F), SD-1-180 (NooLite), SU-1-500 (NooLite) modules.
