"""
Python class for managing all the Arduinos
"""

import threading
import colorama
import serial
import serial.tools.list_ports
from arduinomanager.ArduinoLinker import ArduinoLinker
# pylint: disable=no-name-in-module
from parameters import IGNORE_PORTS

__all__ = ['ArduinosManager']


class ArduinosManager():
    """Python class for managing all the Arduinos"""

    def __init__(self, autodiscover=False):
        self.arduinos = dict()
        self._callback = None
        if autodiscover:
            self.autodiscover()

    @property
    def arduinos_list(self):
        return list(self.arduinos.values())

    @property
    def arduinos_by_identity(self):
        return {arduino.identity: arduino for arduino in self.arduinos_list if arduino.is_identified}
    
    @property
    def arduinos_identified(self):
        return [arduino for arduino in self.arduinos_list if arduino.is_identified]

    def autodiscover(self, ignore_devices=IGNORE_PORTS, verbose=True):
        """
        Search for all devices connected to serial port and add them all
        """
        if verbose:
            print("Detecting connected Arduinos...")
        for com_port in serial.tools.list_ports.comports():
            if not com_port.device in ignore_devices:
                self.add_arduino(com_port.name, com_port.device)
        return len(self.arduinos)

    def add_arduino(self, name, port, autoidentify=True):
        """
        Add an Arduino
        """
        if name in self.arduinos.keys():
            raise ValueError("An arduino with same name already exists")
        self.arduinos[name] = ArduinoLinker(port, name=name)
        self.arduinos[name].set_data_received_callback(self._data_received_callback)
        self.arduinos[name].set_identification_callback(self._arduino_identified_callback)
        self.arduinos[name].start_listening()
        # It seems like it's better to wait a bit after the serial connection has been
        # initialized, otherwise it doesn't seem to work
        if autoidentify:
            #self.arduinos[name].ask_identification()
            threading.Timer(2, self.arduinos[name].ask_identification).start()

    def _data_received_callback(self, arduino_name, data, verbose=True):
        """
        Callback when receiving data from the arduinos
        """
        if verbose:
            print(f"Data received from {arduino_name}: {colorama.Fore.BLUE}{data}{colorama.Style.RESET_ALL}")
        if self._callback:
            self._callback(data)

    def _arduino_identified_callback(self, arduino_name, verbose=True):
        """
        Callback when an arduino has identified itself
        """
        if verbose:
            print(f"{colorama.Fore.GREEN}Arduino {arduino_name} identified as {self.arduinos[arduino_name].identity}{colorama.Style.RESET_ALL}")

    def set_callback(self, callback):
        """
        Set callback to call when receiving data from the arduinos
        """
        self._callback = callback

    def send_command(self, arduinos_target, *args, send_by_identity=True, verbose=True):
        """
        Send a command to a specific (or some specific) Arduino(s)
        """
        arduinos = self.arduinos_by_identity if send_by_identity else self.arduinos
        if type(arduinos_target) is str:
            arduinos_target = [arduinos_target]
        if verbose:
            print(f"Sending{colorama.Fore.YELLOW}", *args, f"{colorama.Style.RESET_ALL}to {colorama.Fore.BLUE}{', '.join(arduinos_target)}{colorama.Style.RESET_ALL}")
        for arduino in arduinos_target:
            try:
                arduinos[arduino].send_command(*args)
            except KeyError:
                print(f"{colorama.Back.RED}Arduino {colorama.Style.BRIGHT}{arduino}{colorama.Style.NORMAL} not identified!{colorama.Style.RESET_ALL}")

    def broadcast(self, *args, identified_only=True, verbose=True):
        """
        Send a command to all Arduinos
        """
        if verbose:
            print(f"{colorama.Fore.BLUE}Broadcasting{colorama.Fore.YELLOW}", *args, colorama.Style.RESET_ALL)
        for arduino in self.arduinos_identified if identified_only else self.arduinos_list:
            arduino.send_command(*args)

    def __del__(self):
        """
        Destructor to close all serial connections of all arduinos at object descruction
        """
        for arduino in self.arduinos:
            arduino.close()
            del arduino
