NooLite-F
=========

Python module to work with NooLite-F (MTRF-64-USB)

Currently implements base commands:

* on - turn power module on
* off - turn power module off
* switch - switch power module state
* load_preset - execute saved preset in power module
* read_state - read state from power module
* set_brightness - set brightness

Each command can accept following parameters:

* channel - channel number to send command. Send command to all power modules assigned with selected channel.
* broadcast - send command in broadcast mode. If True then send command to all power modules assigned with selected channel simultaneously (default - False)
* mode - adapter mode which will used for send command. Can be

  * nooLite TX - uses for nooLite modules (without feedback)
    * nooLite-F TX - uses for nooLite-F modules (with feedback) (default)

In response for each command returns array which contains command result and module info for each power module assigned with selected channel.

Command result equals True if command send successfully, otherwise False.
Module info contains information about module: type, firmware version, state (on/off/temporary on), current brightness and bind mode (on/off)::

    [
        ( True, <ModuleInfo (0x2e25b90), id: 0x52e9, type: 1, hardware: 3, state: 1, brightness: 1.0, mode: 0>),
        (True, <ModuleInfo (0x2e25a90), id: 0x52e3, type: 1, hardware: 3, state: 1, brightness: 1.0, mode: 0>)
    ]

If command result is False, then module info is None.::

    [(False, None)]

Note
====

Tested with MTRF-64-USB adapter and SLF-1-300 power modules.

Example
=======

Exapmpe of usage::

    noolite = NooLiteF(port="COM3")
    noolite.switch(1)
    noolite.switch(channel=1, broadcast=True)
    noolite.switch(channel=1, broadcast=True, mode=Mode.TX)
