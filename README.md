
# DPC3000 Pressure Controller

This repository contains a Python library for controlling the DPC3000 Pressure Controller.

## Installation

To use this library, you'll need to have Python installed on your computer. You can download the latest version of Python from the [official website](https://www.python.org/downloads/).

You'll also need to install the `pyserial` package. You can do this by running the following command:

```
pip install pyserial
```

## Usage

To use this library, you'll need to create an instance of the `PressureController` class. You can do this by importing the class from the `pressure_controller` module and calling its constructor:

```python
from pressure_controller import PressureController

controller = PressureController()
```

Once you have an instance of the `PressureController` class, you can use its methods to control the DPC3000 Pressure Controller. For example, you can use the `read_press` method to read the current pressure value:

```python
pressure = controller.read_press()
print(f"Current pressure: {pressure} bar")
```

You can also use methods like `set_mode`, `stop_press`, and `vent_press` to control the operating mode of the device.

For more information on how to use this library, please refer to the documentation in the `pressure_controller.py` file.

## Contributing

If you'd like to contribute to this project, please feel free to submit a pull request or open an issue on GitHub.

## License

This project is licensed under the MIT License. 
