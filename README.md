# Tello Drones - Python Wrapper

Features:
- Support: **Tello**, **Tello EDU**, **Robomaster TT** (partially, functions for the ESP32 open-source controller not implemented)
- Support: **SDK 2.0** and **SDK 3.0**
- High level functions
- Low level SDK commands using `send_command()`
- Detection of out-of-range values
- User-friendly logs

## Install

```bash
sudo python setup.py install
```

## Usage

```python
from tello import Tello
import time

# create drone object
drone = Tello()

# Connect drone
drone.connect()
# takeoff
drone.takeoff()
# wait 2 secs
time.sleep(2)
# land
drone.land()

```

## Control Commands
---

| Function                                       | Description                                                                                                                                                                                                         | SDK 2.0 | SDK 3.0 |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|---------|
| `connect()`                                    | Initializes the connection to the drone.                                                                                                                                                                            | ✅       | ✅       |
| `takeoff()`                                    | Auto takeoff.                                                                                                                                                                                                       | ✅       | ✅       |
| `lan()`                                        | Auto land.                                                                                                                                                                                                          | ✅       | ✅       |
| `stream_on()`                                  | Enables video stream.                                                                                                                                                                                               | ✅       | ✅       |
| `stream_off()`                                 | Disables video stream.                                                                                                                                                                                              | ✅       | ✅       |
| `emergency()`                                  | Stop Motors immediately.                                                                                                                                                                                            | ✅       | ✅       |
| `reboot()`                                     | Reboot the drone.                                                                                                                                                                                                   |         | ✅       |
| `motor_on()`                                   | Start the motors at low speed and enter in Motor-On mode                                                                                                                                                            |         | ✅       |
| `motor_off()`                                  | Exit Motor-On mode.                                                                                                                                                                                                 |         | ✅       |
| `throw_and_fly()`                              | Launch the drone horizontally within 5s right after executing this function.                                                                                                                                        |         | ✅       |
| `move_up(distance)`                            | Ascend given distance. <br> Parameters: <br> - `distance(int)` in centimeters from 20 to 500                                                                                                                        | ✅       | ✅       |
| `move_down(distance)`                          | Descend given distance. <br> Parameters: <br> - `distance(int)` in centimeters from 20 to 500                                                                                                                       | ✅       | ✅       |
| `move_left(distance)`                          | Fly left given distance. <br> Parameters: <br> - `distance(int)` in centimeters from 20 to 500                                                                                                                      | ✅       | ✅       |
| `move_right(distance)`                         | Fly right given distance. <br> Parameters: <br> - `distance(int)` in centimeters from 20 to 500                                                                                                                     | ✅       | ✅       |
| `move_forward(distance)`                       | Fly forward given distance. <br> Parameters: <br> - `distance(int)` in centimeters from 20 to 500                                                                                                                   | ✅       | ✅       |
| `move_backward(distance)`                      | Moves backward given distance. <br> Parameters: <br> - `distance(int)` in centimeters from 20 to 500                                                                                                                | ✅       | ✅       |
| `rotate_clockwise(angle)`                      | Rotates clockwise given angle. <br> Parameters: <br> - `angle(int)` in degrees from 1 to 360                                                                                                                        | ✅       | ✅       |
| `rotate_counterclockwise(angle)`               | Rotates counterclockwise given angle. <br> Parameters: <br> - `angle(int)` in degrees from 1 to 360                                                                                                                 | ✅       | ✅       |
| `flip(direction)`                              | Flip given direction. <br> Parameters: <br> - `direction(str)` can be `'right'`, `'left'`, `'forward'` and `'backward'`                                                                                             | ✅       | ✅       |
| `go_to(x, y, z, speed)`                        | Fly to given coordinates<sup>[1](#f1)</sup> at given speed . <br> Parameters: <br> - `x(int)` from -500 to 500 <br> - `y(int)` from -500 to 500 <br> - `z(int)` from -500 to 500 <br> - `speed(int)` from 10 to 100 | ✅       | ✅       |
| `joystick_control(roll, pitch, yaw, throttle)` | Sends joystick control commands. <br> Parameters: <br> - `roll(int)` from -100 to 100 <br> - `pitch(int)` from -100 to 100 <br> - `yaw(int)` from -100 to 100 <br> - `throttle(int)` from -100 to 100               | ✅       | ✅       |

<a id="f1">1</a> coordinate system in relation to the body framw and the nose pointing forward:
- `x` forward
- `y` left
- `z` up

## Set Commnands
---

| Function                           | Description                                                                                                                                                                                                                                                                                                                                                                                              | SDK 2.0 | SDK 3.0 |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|---------|
| `set_speed(speed)`                 | Set the current speed to `speed` in cm/s <br> Parameters: <br> - `speed(int)` from 10 to 100                                                                                                                                                                                                                                                                                                             | ✅       | ✅       |
| `set_wifi(ssid, password)`         | Change WiFi name and password <br> Parameters: <br> - `ssid(str)` WiFi name without spaces <br> - `password(str) ` password to connect WiFi                                                                                                                                                                                                                                                              | ✅       | ✅       |
| `set_mission_on()`                 | Enables mission pad. By default, downward detection is enabled                                                                                                                                                                                                                                                                                                                                           | ✅       | ✅       |
| `set_mission_off()`                | Disables mission pad detection.                                                                                                                                                                                                                                                                                                                                                                          | ✅       | ✅       |
| `set_mission_detection(direction)` | Define Before use, you must use the `set_mission_on()` to enable the detection function <br>  Parameters: <br> - `direction(str)` can be `"forward"`, `"downward"` or `"both"`. <br> When either forward-looking or downward-looking detection is enabled alone, the detection frequency is 20Hz. If both enabled, detection will be performed alternatively, with a frequency of 10Hz in each direction | ✅       | ✅       |
| `set_ap(ssid, password)`           | Switch Tello to "Station mode" and connect to WiFi access point <br>  Parameters: <br> - `ssid(str)` WiFi SSID <br> - `password(str)` password to connect WiFi                                                                                                                                                                                                                                           | ✅       | ✅       |
| `set_wifi_channel(channel)`        | Set the WiFi channel of the open-source controller. (Only for Robotmaster TT hardware)                                                                                                                                                                                                                                                                                                                   |         | ✅       |
| `set_video_port(info, video)`      | Set the ports for pushing state information and video streams. Here, `info` is the port for pushing state information, and `video` is the port for pushing video streaming. The range of ports is 1025 to 65535.<br> Parameters: <br> - `info(str)` drone state port <br> - `video(str)` video streaming port                                                                                            |         | ✅       |
| `set_fps(fps)`                     | Set the video stream frame rate. <br> Parameters: <br> - `fps(str)` can be `"high"`, `"middle"`, or `"low"`, indicating `30fps`, `15fps`, and `5fps`, respectively                                                                                                                                                                                                                                       |         | ✅       |
| `set_bitrate(bitrate)`             | Set the video stream bit rate. <br> Parameters: <br> - `bitrate(str)` can be `'auto'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'` indicating `1Mbps`, `2MBps`, `3Mbps`, `4Mbps`, and `5Mbps`                                                                                                                                                                                                                      |         | ✅       |
| `set_resolution(resolution)`       | Set the video stream resolution. <br> Parameters: <br> - `resolution(str)` can be `"high"` or `"low"`, indicating `720P` and `480P`, respectively                                                                                                                                                                                                                                                        |         | ✅       |
| `set_video_direction(direction)`   | Switch camera source for video streaming <br> Parameters: <br> - `direction(str)` can be `"forward"` or `"downward"`                                                                                                                                                                                                                                                                                     |         | ✅       |

## Read Commands
---

| Function                  | Description                                                                                        | Return | SDK 2.0 | SDK 3.0 |
|---------------------------|----------------------------------------------------------------------------------------------------|--------|---------|---------|
| `get_current_set_speed()` | Get current set speed (cm/s) (This is not the current speed) in a range from 10 to 100             | float  | ✅       | ✅       |
| `get_battery()`           | Get current battery percentage in a range from 0 to 100                                            | int    | ✅       | ✅       |
| `get_flight_time()`       | Get motor running time in seconds                                                                  | int    | ✅       | ✅       |
| `get_wifi_snr()`          | Get Wi-Fi SNR (Signal to Noise Ratio)                                                              | int    | ✅       | ✅       |
| `get_sdk_version()`       | Get SDK version. 20 for 2.0 or 30 for 3.0                                                          | int    | ✅       | ✅       |
| `get_serial()`            | Get Tello serial number                                                                            | str    | ✅       | ✅       |
| `get_hardware()`          | Get hardware type. `'TELLO'` or `'RMTT'` (Robomaster TT)                                           | str    |         | ✅       |
| `get_wifi_version()`      | Query the -WiFi version of the open-source controller. (Only applies to 'Robomaster TT')           | str    |         | ✅       |
| `get_ap()`                | Get the name and password of the current router to be connected. (Only applies to 'Robomaster TT') | str    |         | ✅       |
| `get_ssid()`              | Get the current SSID of the drone. (Only applies to 'Robomaster TT')                               | str    |         | ✅       |


## Drone State
---

| Function                                | Description                                                                                                                                                                                                                                                                                                                    | Return      | SDK 2.0 and 3.0 |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|-----------------|
| `get_pad_id()`                          | Get ID of the detected mission pad. <br> - If the mission pad detection function is not enabled, -2 is returned. <br> - If the detection function is enabled but no mission pad is detected, -1 is returned                                                                                                                    | int         | ✅               |
| `get_x()` <br> `get_y()` <br> `get_z()` | Get the `x` `y` `z` coordinates respectively, relative to the detected mission pad, in **centimeters**. <br> - If the mission pad detection function is not enabled, -200 is returned. <br> - If the detection function is enabled but no mission pad is detected, -100 is returned.                                           | int         | ✅               |
| `get_pad_coord()`                       | Get **list** of coordinates in format [x, y, z] of the drone relative to the detected mission pad, in **centimeters** <br> - If the mission pad detection function is not enabled, [-200, -200, -200] is returned. <br> - If the detection function is enabled but no mission pad is detected, [-100, -100, -100] is returned. | list(int)   | ✅               |
| `get_pad_orientation()`                 | Get **list** of angles in format [roll, pitch, yaw] of the drone relative to the detected mission pad, in **degrees**                                                                                                                                                                                                          | list(int)   | ✅               |
| `get_pitch()`                           | Get pitch angle in **degrees** (relative to the initial orientation at the moment of turn on the drone)                                                                                                                                                                                                                        | int         | ✅               |
| `get_roll()`                            | Get roll angle in **degrees** (relative to the initial orientation at the moment of turn on the drone)                                                                                                                                                                                                                         | int         | ✅               |
| `get_yaw()`                             | Get yaw angle in **degrees** (relative to the initial orientation at the moment of turn on the drone)                                                                                                                                                                                                                          | int         | ✅               |
| `get_orientation()`                     | Get orientation angles in format [roll, pitch, yaw] relative to the initial orientation at the moment of turn on the drone.                                                                                                                                                                                                    | list(int)   | ✅               |
| `get_speed_x()`                         | Get x-axis speed in dm/s *(decimeter per second)                                                                                                                                                                                                                                                                               | int         | ✅               |
| `get_speed_y()`                         | Get y-axis speed in dm/s *(decimeter per second)                                                                                                                                                                                                                                                                               | int         | ✅               |
| `get_speed_z()`                         | Get z-axis speed in dm/s *(decimeter per second)                                                                                                                                                                                                                                                                               | int         | ✅               |
| `get_speed()`                           | Get **list** of linear velocities in format [vel_x, vel_y, vel_z] *(decimeter per second)                                                                                                                                                                                                                                      | list(int)   | ✅               |
| `get_min_temp()`                        | Get the minimum temperature of the main board in degrees celsius                                                                                                                                                                                                                                                               | int         | ✅               |
| `get_max_temp()`                        | Get the maximum temperature of the main board in degrees celsius                                                                                                                                                                                                                                                               | int         | ✅               |
| `get_tof_distance()`                    | Get the distance from the bottom of the drone to the ground (using the ToF sensor) in **centimeter**. <br> - Measuring range is from 30 to 900 cm <br> - If the sensor is out of range, it returns 0                                                                                                                           | int         | ✅               |
| `get_height()`                          | Get drone height in cm relative to take-off point                                                                                                                                                                                                                                                                              | int         | ✅               |
| `get_baro()`                            | Get height detected by barometer in meters (absolute height)                                                                                                                                                                                                                                                                   | float       | ✅               |
| `get_time()`                            | Get motor running time in seconds                                                                                                                                                                                                                                                                                              | float       | ✅               |
| `get_acc_x()`                           | Get x-axis acceleration cm/s2                                                                                                                                                                                                                                                                                                  | float       | ✅               |
| `get_acc_y()`                           | Get y-axis acceleration cm/s2                                                                                                                                                                                                                                                                                                  | float       | ✅               |
| `get_acc_z()`                           | Get z-axis acceleration cm/s2                                                                                                                                                                                                                                                                                                  | float       | ✅               |
| `get_acceleration()`                    | Get **list** of accelerations for `x` `y` and `z` in format [acc_x, acc_y, acc_z] cm/s2                                                                                                                                                                                                                                        | list(float) | ✅               |

## Video Functions

| Function              | Description                              | SDK 2.0 and 3.0 |
|-----------------------|------------------------------------------|-----------------|
| `read_frame()`        | Read last frame from the video streaming | ✅               |
| `bgr8_to_jpeg(value)` | Convert from `bgr8` to `jpeg`            | ✅               |

## External Resources
- [Tello SDK 2.0 - Official User Guide](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [ROBOMASTER TT SDK 3.0 - Official User Guide](https://dl.djicdn.com/downloads/RoboMaster+TT/Tello_SDK_3.0_User_Guide_en.pdf)
- [Tello - User Guide](https://dl.djicdn.com/downloads/RoboMaster+TT/Tello_SDK_3.0_User_Guide_en.pdf)
