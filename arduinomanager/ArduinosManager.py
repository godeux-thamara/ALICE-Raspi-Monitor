"""
Python class for managing all the Arduinos
"""

import threading
import colorama
import serial
import serial.tools.list_ports
from arduinomanager.ArduinoLinker import ArduinoLinker

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
        return self.arduinos.values()

    @property
    def arduinos_by_identity(self):
        return {arduino.identity: arduino for arduino in self.arduinos_list if arduino.is_identified}

    def autodiscover(self):
        """
        Search for all devices connected to serial port and add them all
        """
        for com_port in serial.tools.list_ports.comports():
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

    def send_command(self, arduino_name, *args, send_by_id=True, verbose=True):
        """
        Send a command to a specific (or some specific) Arduino(s)
        """
        arduinos = self.arduinos_by_identity if send_by_id else self.arduinos
        if type(arduino_name) is str:
            arduino_name = [arduino_name]
        if verbose:
            print(f"Sending{colorama.Fore.YELLOW}", *args, f"{colorama.Style.RESET_ALL}to {colorama.Fore.BLUE}{', '.join(arduino_name)}{colorama.Style.RESET_ALL}")
        for arduino in arduino_name:
            arduinos[arduino].send_command(*args)

    def broadcast(self, *args, verbose=True):
        """
        Send a command to all Arduinos
        """
        if verbose:
            print(f"{colorama.Fore.BLUE}Broadcasting{colorama.Fore.YELLOW}", *args, colorama.Style.RESET_ALL)
        for arduino in self.arduinos.values():
            arduino.send_command(*args)

    def __del__(self):
        """
        Destructor to close all serial connections of all arduinos at object descruction
        """
        for arduino in self.arduinos:
            arduino.close()
            del arduino
