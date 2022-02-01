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

- `takeoff()`
- `land()`
- `streamon()`
- `streamoff()`
- `emergency()`
- `move_up(distance(in centimeters from 20 to 500))`
- `move_down(distance(in centimeters from 20 to 500))`
- `move_left(distance(in centimeters from 20 to 500))`
- `move_forward(distance(in centimeters from 20 to 500))`
- `move_backward(distance(in centimeters from 20 to 500))`
- `rotate_clockwise(degrees(in degrees from 1 to 360))`
- `rotate_counterclockwise(degrees(in degrees from 1 to 360))`
- `flip('right'/'left'etc)`

### Set Commnands

- `set_speed(50)`
    - parameters: `speed` (int) from 10 to 100
- `set_wifi('WIFI-name'(without spaces), 'pass')`
    - parameters: `ssid`, `password`
- `set_mission_on()`
- `set_mission_off()`
- `set_mission_detection('downward')`
    - parameters: `direction` 0: downward detection enabled. 1: forward detection enabled. 2: both forward and downward detection enabled
- `set_ap('Access point name', 'pass')`
    - parameters: `ssid`, `password`
- `set_wifi_channerl(channel)` (Only for Robotmaster TT hardware)
    - parameters: `channel`
    - only supported on SDK 3.0
- `set_video_port(info='1234', video='5678')`
    - parameters: `info`, `video`
    - only supported on SDK 3.0
- `set_fps("high")` can be `"high"`, `"middle"`, or `"low"`, indicating 30fps, 15fps, and 5fps, respectively
    - parameters: `fps`
    - only supported on SDK 3.0
- `set_bitrate('auto')`
    - parameters: `bitrate` options: 'auto', '1', '2', '3', '4', '5' indicating 1Mbps, 2MBps, 3Mbps, 4Mbps, and 5Mbps
    - only supported on SDK 3.0
- `set_resolution("high")` can be "high" or "low", indicating 720P and 480P, respectively
    - parameters: `resolution`
    - only supported on SDK 3.0

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
