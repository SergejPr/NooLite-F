NooLite-F
=========

Python module to work with NooLite-F (MTRF-64-USB)

Supported commands:

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
* mode - mode of the command sending. TX - for nooLite module (without feedback), TX_F - for nooLite-F modules (with feedback).

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

Note
====

Tested with MTRF-64-USB adapter and SLF-1-300, SD-1-180, SU-1-500 modules.

Example
=======

Example of usage::

    noolite = NooLiteF(port="COM3")
    noolite.switch(1)
    noolite.switch(1, broadcast=True)
    noolite.switch(1, broadcast=True, mode=Mode.TX_F)
