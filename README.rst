NooLite-F
=========

Python module to work with NooLite-F (MTRF-64-USB)
You can find more details about MTRF-64-USB api on official NooLite site:

* https://www.noo.com.by/
* https://www.noo.com.by/assets/files/PDF/nooLite%20API_v1.0.pdf
* https://www.noo.com.by/assets/files/PDF/MTRF-64-USB.pdf


Send commands to modules
========================

There are possible three ways of sending commands to modules:


Using adapter
-------------
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


Using controller
----------------

You can use MTRF64Controller and abstract from manual request data creating. Just call appropriate function::

    controller = MTRF64Controller("COM3")
    controller.set_brightness(channel=60, brightness=0.3, module_mode=ModuleType.NOOLITE)

    controller.switch(module_id=0x5435, module_mode=ModuleType.NOOLITE-F)


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
- module_mode: module work mode, used to determine adapter mode for send command (default - NOOLITE_F).

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


Using module wrappers
---------------------
You can use special classes that are wrappers around controller. Each class is representation of the
concrete module or modules assigned with specific channel::

    controller = MTRF64Controller("COM3")
    dimmer = Dimmer(controller, 62, ModuleType.NOOLITE)
    dimmer.set_brightness(0.4)

    switch = Switch(controller, channel=60, ModuleType.NOOLITE)
    switch.on()

    switch = Switch(controller, module_id=0x5023, ModuleType.NOOLITE_F)
    switch.switch()


Available module wrappers:

* **Switch** - supports on/off, toggle, preset. Also supports services methods for bind/unbind.
* **ExtendedSwitch** - In additional to Switch, supports temporary on.
* **Dimmer** - In additional to ExtendedSwitch supports brightness managing.
* **GBLed** - supports toggle, brightness management, rgb color management.

Receiving commands from remote controls
=======================================

You can also use several ways to receive data from remote controllers and sensors.


Using adapter listener
----------------------

You can receive data from remote controllers using MTRF64USBAdapter directly. For it you should pass a listener method into adapter constructor.
This method will be call each time when adapter get data from sensors or remote controls::

    def on_receive_data(incoming_data: IncomingData):
        print("data: {0}".format(incoming_data))

    adapter = MTRF64USBAdapter("COM3", on_receive_data)


Using controller listener
-------------------------

You can create special command listener and assign it with concrete channel in controller. The controller get incoming data, handle it and call appropriate method in listener.
So you should not worry about it::

    controller = MTRF64Controller("COM3")
    switch = Dimmer(controller, channel=62, ModuleType.NOOLITE)

    class MyRemoteController(RemoteControllerListener):

        def on_on(self):
            switch.on()

        def on_off(self):
            switch.off()

        def on_switch(self):
            switch.switch()

        def on_brightness_tune(self, direction: BrightnessDirection):
            switch.brightness_tune(direction)

        def on_brightness_tune_stop(self):
            switch.brightness_tune_stop()

        def on_brightness_tune_back(self):
            switch.brightness_tune_back()


    class MySensor(RemoteControllerListener):
        def on_temp_humi(self, temp: float, humi: int, battery: BatteryState, analog: float):
            print("temp: {0}, humidity: {1}".format(temp, humi))


    remoteController = MyRemoteController()
    sensor = MySensor()

    controller.add_listener(1, remoteController)
    controller.add_listener(2, remoteController)


Using sensor wrappers
---------------------

And in the end you can use a special wrappers around Controller and RemoteControllerListener. Just create it, set channel and appropriate listeners::

    def on_temp(temp, humi, battery, analog):
        print("temp: {0}, humi: {1}, battery_state: {2}, analog: {3}".format(temp, humi, battery, analog))

    def on_battery():
        print("battery")

    def on_switch():
        print("switch")

    def on_tune_back():
        print("tune back")

    def on_tune_stop():
        print("tune stop")

    def on_roll_color():
        print("roll color")

    def on_switch_color():
        print("switch color")

    def on_switch_mode():
        print("switch mode")

    def on_switch_speed():
        print("switch speed")


    controller = MTRF64Controller("COM3")

    tempSensor = TempHumiSensor(controller, 9, on_temp, on_battery)
    rgb = RGBRemoteController(controller, 63, on_switch, on_tune_back, on_tune_stop, on_roll_color, on_switch_color, on_switch_mode, on_switch_speed, on_battery)


Available wrappers:

* **TempHumiSensor** - supports receiving data from temperature and humidity sensors.
* **MovingDetector** - supports receiving data from movement detector.
* **RemoteController** - supports receiving commands from standard NooLite remote controllers.
* **RGBRemoteController** - supports receiving commands from RGB Remote controller.


Note
====

Tested with MTRF-64-USB adapter and modules:

* SLF-1-300 (NooLite-F, switch module)
* SRF-1-3000 (NooLite-F, smart power socket)
* SD-1-180 (NooLite, RGB Module)
* SU-1-500 (NooLite, switch module)
* PM112 (NooLite, moving detector)
* PT111 (NooLite, temperature and humidity sensor)
* PB211 (NooLite, remote controller)
* PU112-2 (NooLite, RGB remote controller)

