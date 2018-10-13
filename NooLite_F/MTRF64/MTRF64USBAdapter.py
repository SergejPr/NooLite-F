import logging

from enum import IntEnum
from serial import Serial
from struct import Struct
from time import sleep

from threading import *
from queue import Queue, Empty


class Command(IntEnum):
    OFF = 0,
    BRIGHT_DOWN = 1,
    ON = 2,
    BRIGHT_UP = 3,
    SWITCH = 4,
    BRIGHT_BACK = 5,
    SET_BRIGHTNESS = 6,
    LOAD_PRESET = 7,
    SAVE_PRESET = 8,
    UNBIND = 9,
    STOP_BRIGHT = 10,
    BRIGHT_STEP_DOWN = 11,
    BRIGHT_STEP_UP = 12,
    BRIGHT_REG = 13,
    BIND = 15,
    ROLL_COLOR = 16,
    SWITCH_COLOR = 17,
    SWITCH_MODE = 18,
    SPEED_MODE = 19,
    BATTERY_LOW = 20,
    SENS_TEMP_HUMI = 21,
    TEMPORARY_ON = 25,
    MODES = 26,
    READ_STATE = 128,
    WRITE_STATE = 129,
    SEND_STATE = 130,
    SERVICE = 131,
    CLEAR_MEMORY = 132


class Mode(IntEnum):
    TX = 0,
    RX = 1,
    TX_F = 2,
    RX_F = 3,
    SERVICE = 4,
    FIRMWARE_UPDATE = 5


class ResponseCode(IntEnum):
    SUCCESS = 0,
    NO_RESPONSE = 1,
    ERROR = 2,
    BIND_SUCCESS = 3


class Action(IntEnum):
    SEND_COMMAND = 0,
    SEND_BROADCAST_COMMAND = 1,
    READ_RESPONSE = 2,
    BIND_MODE_ON = 3,
    BIND_MODE_OFF = 4,
    CLEAR_CHANNEL = 5,
    CLEAR_MEMORY = 6,
    UNBIND_ADDRESS_FROM_CHANNEL = 7,
    SEND_COMMAND_TO_ID_IN_CHANNEL = 8,
    SEND_COMMAND_TO_ID = 9


class IncomingDataException(Exception):
    """Base class for response exceptions."""


class OutgoingData(object):
    mode: Mode = Mode.TX
    action: Action = Action.SEND_COMMAND
    channel: int = 0
    command: Command = Command.OFF
    format: int = 0
    data: bytearray = bytearray(4)
    id: int = 0

    def __repr__(self):
        return "<Request (0x{0:x}), mode: {1}, action: {2}, channel: {3:d}, command: {4:d}, format: {5:d}, data: {6}, id: 0x{7:x}>"\
            .format(id(self), self.mode, self.action, self.channel, self.command, self.format, self.data, self.id)


class IncomingData(object):
    mode: Mode = None
    status: ResponseCode = None
    channel: int = None
    command: Command = None
    count: int = None
    format: int = None
    data: bytearray = None
    id: int = None

    def __repr__(self):
        return "<Response (0x{0:x}), mode: {1}, status: {2}, packet_count: {3} channel: {4:d}, command: {5:d}, format: {6:d}, data: {7}, id: 0x{8:x}>"\
            .format(id(self), self.mode, self.status, self.count, self.channel, self.command, self.format, self.data, self.id)


_LOGGER = logging.getLogger("MTRF64USBAdapter")
_LOGGER.setLevel(logging.DEBUG)
_LOGGER_HANDLER = logging.StreamHandler()
_LOGGER_HANDLER.setFormatter(logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S"))
_LOGGER.addHandler(_LOGGER_HANDLER)


class MTRF64USBAdapter(object):
    _packet_size = 17
    _serial = None
    _read_thread = None
    _command_response_queue = Queue()
    _incoming_queue = Queue()
    _send_lock = Lock()
    _listener_thread = None
    _listener = None
    _is_released = False

    def __init__(self, port: str, on_receive_data=None):
        self._serial = Serial(baudrate=9600)
        self._serial.port = port
        self._serial.open()

        self._listener = on_receive_data

        self._read_thread = Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self._read_thread.start()

        self._listener_thread = Thread(target=self._read_from_incoming_queue)
        self._listener_thread.daemon = True
        self._listener_thread.start()

    def release(self):
        self._is_released = True
        self._serial.close()
        self._incoming_queue.put(None)
        self._listener = None

    def send(self, data: OutgoingData) -> [IncomingData]:
        responses = []

        packet = self._build(data)
        with self._send_lock:
            _LOGGER.warning("Send:\n - request: {0},\n - packet: {1}".format(data, packet))
            self._command_response_queue.queue.clear()
            self._serial.write(packet)

            try:
                while True:
                    response = self._command_response_queue.get(timeout=2)
                    responses.append(response)
                    if response.count == 0:
                        break

            except Empty as err:
                _LOGGER.error("Error receiving response: {0}.".format(err))

            # For NooLite.TX we should make a bit delay. Adapter send the response without waiting until command was delivered.
            # So if we send new command until previous command was sent to module, adapter will ignore new command. Note:
            if data.mode == Mode.TX or data.mode == Mode.RX:
                sleep(0.2)

        return responses

    # Private
    def _crc(self, data) -> int:
        sum = 0
        for i in range(0, len(data)):
            sum = sum + data[i]
        sum = sum & 0xFF
        return sum

    def _build(self, data: OutgoingData) -> bytes:
        format_begin = Struct(">BBBBBBB4sI")
        format_end = Struct("BB")

        packet = format_begin.pack(171, data.mode, data.action, 0, data.channel, data.command, data.format, data.data, data.id)
        packet_end = format_end.pack(self._crc(packet), 172)

        packet = packet + packet_end

        return packet

    def _parse(self, packet: bytes) -> IncomingData:
        if len(packet) != self._packet_size:
            raise IncomingDataException("Invalid packet size: {0}".format(len(packet)))

        format = Struct(">BBBBBBB4sIBB")

        data = IncomingData()
        start_byte, data.mode, data.status, data.count, data.channel, data.command, data.format, data.data, data.id, crc, stop_byte = format.unpack(packet)

        if (start_byte != 173) or (stop_byte != 174) or (crc != self._crc(packet[0:-2])):
            raise IncomingDataException("Invalid response")

        return data

    def _read_loop(self):
        while True:
            packet = self._serial.read(self._packet_size)

            if self._is_released:
                break

            try:
                data = self._parse(packet)
                _LOGGER.warning("Receive:\n - packet: {0},\n - data: {1}".format(packet, data))

                if data.mode == Mode.TX or data.mode == Mode.TX_F:
                    self._command_response_queue.put(data)
                elif data.mode == Mode.RX or data.mode == Mode.RX_F:
                    self._incoming_queue.put(data)
                else:
                    pass

            except IncomingDataException as err:
                _LOGGER.error("Packet error: {0}".format(err))
                pass

    def _read_from_incoming_queue(self):
        while True:
            input_data = self._incoming_queue.get()

            if self._is_released:
                break

            if self._listener is not None:
                self._listener(input_data)
