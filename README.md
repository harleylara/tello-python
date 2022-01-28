# Tello SDK 2.0 - Python Wrapper

[Tello SDK 2.0 Official User Guide](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
[Robomaster TT SDK 3.0 Offial User Guide](https://dl.djicdn.com/downloads/RoboMaster+TT/Tello_SDK_3.0_User_Guide_en.pdf)

## Install

```bash
./install.sh
```

## Usage

```python
from tello import Tello

# create drone object
drone = Tello()

# Connect drone
drone.connect()
```

### Control Commands


### Set Commnands


### Read Commands

| Function             | Description                                                                                        | Return | SDK 2.0 | SDK 3.0 |
| -------------------- | -------------------------------------------------------------------------------------------------- | ------ | ------- | ------- |
| `get_speed()`        | Get current set speed (cm/s) (This is not the current speed) in a range from 10 to 100             | float  | ✅      | ✅      |
| `get_battery()`      | Get current battery percentage in a range from 0 to 100                                            | int    | ✅      | ✅      |
| `get_time()`         | Get motor running time in seconds                                                                  | int    | ✅      | ✅      |
| `get_wifi_snr()`     | Get Wi-Fi SNR (Signal to Noise Ratio)                                                              | int    | ✅      | ✅      |
| `get_sdk_version()`  | Get SDK version. 20 for 2.0 or 30 for 3.0                                                          | int    | ✅      | ✅      |
| `get_serial()`       | Get Tello serial number                                                                            | str    | ✅      | ✅      |
| `get_hardware()`     | Get hardware type. `'TELLO'` or `'RMTT'` (Robomaster TT)                                           | str    |         | ✅      |
| `get_wifi_version()` | Query the -WiFi version of the open-source controller. (Only applies to 'Robomaster TT')           | str    |         | ✅      |
| `get_ap()`           | Get the name and password of the current router to be connected. (Only applies to 'Robomaster TT') | str    |         | ✅      |
| `get_ssid()`         | Get the current SSID of the drone. (Only applies to 'Robomaster TT')                               | str    |         | ✅      |
