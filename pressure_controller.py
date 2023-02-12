"""
Script for controlling the Pressure Controller
"""
from __future__ import print_function

import time
from typing import Optional

import serial
import serial.tools.list_ports

import constants as ct


class PressureController:
    """Class for the DPC3000 pressure controller"""

    def __init__(self, port_name: str = "COM5", baudrate: int = 9600, timeout: int = 1):
        self.port_name = port_name
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.open_serial_port()
        self.com_dict = {}

    def open_serial_port(self):
        """Opens the serial port specified by the `PORT_NAME` attribute."""
        try:
            self.ser = serial.Serial(
                self.port_name, baudrate=self.baudrate, timeout=self.timeout
            )
            print(f"Serial port {self.port_name} opened")
            time.sleep(0.5)
            return True
        except serial.SerialException as var:
            print(f"Serial port {self.port_name} could not be opened")
            print(f"Exception Details: {var}")
            return False

    def read_mode(self, info: bool = False) -> str:
        """Returns the current operating mode (Control, Measure or Vent)."""
        mode_read = ct.READMODE.encode("ascii")
        self.ser.write(mode_read)
        mode = self.ser.readline().decode("ascii").rstrip("\r")
        if info:
            message = f"Device in {mode} mode."
            print(f"Info: {message}")
        return mode

    def __del__(self):
        """Close the serial port when the object is deleted."""
        if self.ser is not None:
            self.ser.close()
            print(f"Serial port {self.port_name} closed")

    def __repr__(self):
        """Return a string representation of the object."""
        return f"PressureController(port_name={self.port_name}, baudrate={self.baudrate}, timeout={self.timeout})"

    def set_mode(self, mode: str = "Control") -> None:
        """
        Switches the current operating mode (Mode: Control, Measure, Vent).

        Args:
        - mode: str, the desired mode of operation, default to "Control".
        """
        if mode in ct.MODES:
            self.ser.write((ct.SETMODE + mode + "\r").encode("ascii"))
            time.sleep(0.1)
        else:
            print("Please choose a correct mode [Control, Measure, Vent]")

    def stop_press(self, info: bool = False) -> None:
        """
        Stops the controller.

        Args:
        - info: bool, optional argument to enable print statement.
        """
        if info:
            print("Stop controller command was sent.")

        read_pressure = ct.STOP.encode("ascii")
        self.ser.write(read_pressure)
        self.ser.readline().decode("ascii")

        if info:
            print("Controller stopped.")

    def vent_press(self, info: bool = False):
        """The controller vents to the environment."""
        if info:
            actual_press = self.read_press(False)
            message = f"Start venting the pressure from {actual_press} bar."
            print(f"INFO: {message}. Please wait ...")

        self.ser.write(ct.VENT.encode("ascii"))
        self.ser.readline().decode("ascii")

        status = self.read_status(binar=False, info=False)
        while status & 8:
            status = self.read_status(binar=False, info=False)

        if info:
            final_press = self.read_press(False)
            message = f"Venting finished, reached to {final_press} bar ..."
            print(f"INFO: {message}")

    def read_status(self, binar: bool = False, info: bool = True):
        """Returns the state of the controller’s state machine."""
        if binar:
            self.ser.write(ct.READSTATUS_BIN.encode("ascii"))
            time.sleep(0.2)
            status = self.ser.readline().decode("ascii")
        else:
            self.ser.write(ct.READSTATUS.encode("ascii"))
            time.sleep(0.2)
            status = self.ser.readline().decode("ascii")

        status = str(status[:-1])

        if info:
            message = f"Controller status :: {str(status)}"
            print(f"INFO: {message}")

        if binar:
            return int(status, 2)
        else:
            return int(status)

    def set_press(
        self,
        press_value: float = 1.0,
        info: bool = False,
        show_status_change: bool = True,
    ) -> float:
        """Set pressure"""
        if info:
            message = f"Set pressure value: {press_value} bar"
            print(f"INFO: {message}")
        self.set_mode()

        set_pressure = (ct.SETPRESS + str(press_value) + "\r").encode("ascii")
        self.ser.write(set_pressure)
        time.sleep(0.2)
        pressure_read_value = self.read_press()
        status = self.read_status()
        self.translate_status(status)

        while (
            abs(pressure_read_value - press_value) > ct.PRECISSION
        ) and not status & 1:
            time.sleep(0.1)
            pressure_read_value = self.read_press(info)

            if show_status_change:
                new_status = self.read_status(info=False)
                if new_status != status:
                    self.translate_status(status)

            status = self.read_status(info=False)
            if (status & 64) or (status & 128):
                self.translate_status(status)
                return pressure_read_value

        pressure_read_value = self.read_press(info=False)
        print(f"Pressure reached target value of {pressure_read_value}!")
        return pressure_read_value

    def read_press(self, info: bool = True) -> float:
        """Returns the actual pressure value"""
        read_pressure = ct.READPRESS.encode("ascii")
        self.ser.write(read_pressure)
        response = self.ser.readline().decode("ascii")
        response = response.replace(",", ".")
        if info:
            message = f"Read pressure value: {str(response)} bar"
            print(f"INFO: {message}")

        return float(response)

    def press_connection(self, info: bool = False) -> str:
        """Check connection between the serial port and the controller"""
        if info:
            message = "Check communication between DPC3000 and host"
            print(f"INFO: {message}")

        self.ser.write(b"@check\r")
        response = ""
        try:
            response = self.ser.readline().decode("ascii")
            print(f"DPC3000 response: {response}")
        except serial.SerialException as err:
            print("Exception Details: ", err)

        self.serial_stop()
        return response

    def tick_press(self, steps: int = 1) -> None:
        """The pressure valve is opened for a brief moment (pressure pulse duration).
        Around 0.001 bar are set"""
        for _ in range(steps):
            time.sleep(0.2)
            self.ser.write("@tp\r".encode("ascii"))

    def tick_vac(self, steps: Optional[int] = 0) -> None:
        """The vacuum / venting valve is opened for a brief moment (vacuum pulse duration)."""
        self.ser.write(ct.TICKVAC.encode("ascii"))
        if steps > 0:
            for _ in range(steps):
                time.sleep(0.2)
                self.ser.write("@tp\r".encode("ascii"))

    # SERIAL Communication functions
    def serial_config(self):
        """
        Function to get the serial port configuration
        """
        serial_param = {
            "port": self.ser.port,
            "baudrate": self.ser.baudrate,
            "bytesize": self.ser.bytesize,
            "parity": self.ser.parity,
            "stop bits": self.ser.stopbits,
        }

        print("param".ljust(15), "value")
        for key, value in serial_param.items():
            print(str(key).ljust(15), str(value))

        return serial_param

    def serial_stop(self, info: bool = False):
        """
        Function to stop the serial communication
        """
        self.ser.close()
        if info:
            print("Serial communication stopped !!")

    def serial_ports(self):
        """List all available serial ports"""
        port_list = list(serial.tools.list_ports.comports())
        for port in port_list:
            self.com_dict[str(port[0])] = str(port[1])

        if len(self.com_dict) == 0:
            print("No COM/serial ports")
        else:
            table = []
            for key, value in list(self.com_dict.items()):
                table.append([key, value])
            print("Port", "Details")
            for row in table:
                print(row[0], row[1])

        return self.com_dict

    # Helper functions

    def pretty(self, dictio, indent=0):
        """Prints a nested dictionary in a readable format"""
        for key, value in list(dictio.items()):
            print("\t" * indent + str(key))
            if isinstance(value, dict):
                self.pretty(value, indent + 1)
            else:
                print("\t" * (indent + 1) + str(value))

    def translate_status(self, received_status: int):
        """Translates status of bits"""
        if received_status in ct.PRESS_STATUS:
            status = ct.PRESS_STATUS.get(received_status, "ukn")
            print("\t\tStatus:", status)
            return

        def what_bit_is_set(n, k):
            """
            Checks if the kth bit is set. 
            https://www.geeksforgeeks.org/check-whether-k-th-bit-set-not/
            """
            tmp = n & (1 << (k - 1))
            if tmp:
                _status = ct.PRESS_STATUS.get(tmp, "ukn")
                print("\t\tStatus:", _status)

        for i in range(8):
            what_bit_is_set(received_status, i + 1)


if __name__ == "__main__":
    controller = PressureController()
    # mode = controller.read_mode(info=True)
    # print(mode)
    controller.serial_ports()
