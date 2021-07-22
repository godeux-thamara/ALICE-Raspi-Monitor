"""
Python class for communication with an Arduino via Serial
"""

import threading
import time
import serial
# pylint: disable=no-name-in-module
from parameters import BAUDRATE

__all__ = ['ArduinoLinker']


class ArduinoLinker():
    """Python class for communication with an Arduino via Serial"""

    def __init__(self, port, baudrate=BAUDRATE, name=None, auto_identification=False, autostart_listening=False):
        self._serial = serial.Serial(port, baudrate)
        self.name = name
        self.listening = False
        self.lock = threading.RLock()

        self._identity = None
        self._identification_callback = None
        self._data_received_callback = None
        self._listening_thread = None

        if auto_identification:
            self.ask_identification()
        if autostart_listening:
            self.start_listening()

    @property
    def port(self):
        """Port used for the serial connection"""
        return self._serial.port

    @property
    def baudrate(self):
        """Baudrate of the serial connection"""
        return self._serial.baudrate

    @property
    def identity(self):
        """Identity sent by the Arduino, or None if the Arduino has not authentified itself yet"""
        return self._identity

    @property
    def is_identified(self):
        """
        True if the Arduino as identified itself, False otherwise
        """
        return bool(self._identity)

    def close(self):
        """
        Close the serial connection
        """
        return self._serial.close()

    def is_open(self):
        """
        Return True if the serial connection is currently open, False otherwise
        """
        return self._serial.is_open()

    def send_string(self, command):
        """
        Send a string and a newline character thru the serial connection
        """
        with self.lock:
            return self._serial.write((command + "\n").encode())

    def send_command(self, *args):
        """
        Send a command along with its arguments thru the serial connection
        """
        return self.send_string(("{} "*len(args)).format(*args).rstrip())

    def _readline(self):
        """
        Wait for the next complete line received from serial. Blocking.
        """
        return self._serial.readline().decode().lstrip().rstrip()

    def set_data_received_callback(self, callback):
        """
        Set the callback to call when data is received from the Arduino
        """
        self._data_received_callback = callback

    def set_identification_callback(self, callback):
        """
        Set the callback to call when the arduino has identified itself
        """
        self._identification_callback = callback

    def ask_identification(self):
        """
        Ask the Arduino to identify itself
        """
        return self.send_command("identify")

    def _identify(self, line):
        """
        Check if `line` is an identification command, and set the `identity` attribute if necessary.
        Return True if identity was set, False otherwise
        """
        if line.startswith("identity "):
            self._identity = line.lstrip("identity ").rstrip()
            if self._identification_callback:
                self._identification_callback(self.name)
            return True
        return False

    def listen(self):
        """
        Listen for data from the Arduino and send them to _callback. Blocking
        """
        while self.listening:
            if self._data_received_callback and self._serial.in_waiting:
                line = self._readline()
                self._identify(line) or self._data_received_callback(self.name, line)
            else:
                time.sleep(.01)

    def start_listening(self):
        """
        Start a new thread for listening data from the Arduino. Non blocking.
        """
        self.listening = True
        self._listening_thread = threading.Thread(target=self.listen, name=f"ListeningThread-{self.name}", daemon=True)
        self._listening_thread.start()

    def stop_listening(self):
        """
        Stop the listening thread
        """
        self.listening = False

    def __repr__(self):
        return f"<ArduinoLinker arduino_name={self.name} identity={self.identity}>"

    def __del__(self):
        """
        Destructor to close the serial connection at object descruction
        """
        self._serial.close()
