import socket
from threading import Thread
import logging
import time
from typing import Optional, Union, Type, Dict

# Multi thread implementation
# thread 1: For send control command and receive response
# thread 2: For receive Tello State
threads_initialized = False

# Drones Dictionary
# useful for swarm instancing
drones: Optional[dict] = {}

# UDP client for send commands and receive response
client_socket: socket.socket

class Tello:

    """Python Wrapper for 'Tello' drone, 'Tello EDU' and 'Robomaster TT'

    Support:
        SDK 2.0 and 3.0
    """

    # localtello_ip
    LOCAL_IP = '0.0.0.0'
    # Tello IP address
    TELLO_IP = '192.168.10.1'
    # UDP port for send and receive response
    TELLO_PORT = 8889

    # Tello State
    # UDP por for receive Tello State
    STATE_UDP_PORT = 8890
    
    # State fields in Int data type
    INT_STATE_FIELDS = (
        # Mission pads enabled only in Tello EDU
        'mid',                  # pad ID
        'x', 'y', 'z',          # cm
        
        # Common entries
        'pitch', 'roll', 'yaw', # degree
        'vgx', 'vgy', 'vgz',    # cm/s
        'templ', 'temph',       # Celsius
        'tof', 'h',             # cm
        'bat',                  # percentage
        'time'                  # s
    )

    # State fields in Float data type
    FLOAT_STATE_FIELDS = (
            'baro',             # cm
            'agx', 'agy', 'agz' # cm/s^2
    )

    state_field_converters: Dict[str, Union[Type[int], Type[float]]]
    state_field_converters = {key : int for key in INT_STATE_FIELDS}
    state_field_converters.update({key : float for key in FLOAT_STATE_FIELDS})

    # Constants for failure handling
    TIMEOUT = 8
    TIME_BTW_COMMANDS = 0.1
    # number of retries after a failed command
    RETRY_COUNT = 3 

    client_socket_up = False

    # Logger
    HANDLER = logging.StreamHandler()
    FORMATTER = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s - %(message)s')
    HANDLER.setFormatter(FORMATTER)

    LOGGER = logging.getLogger('tello-drone')
    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(logging.DEBUG)
    
    sdk_mode_enable = False
    # SDK version can be 20 for 2.0 or 30 for 3.0
    sdk_version = None
    # Hardware can be 'TELLO' or 'RMTT'
    hardware = None

    mission_mode_enable = False
    MISSION_DETECTION_DIRECTION = {
        'downward': 0,
        'forward': 1,
        'both': 2,
    }

    SET_SPEED = {
        "low": 10,
        "mid": 50,
        "high": 100
    }

    SPEED_RANGE = (
        10,
        100
    )
    
    SET_FPS = (
        "high",
        "middle",
        "low"
    )

    SET_BITRATE = {
        "auto": 0,  # auto
        '1': 1,  # 1Mbps
        '2': 2,  # 2Mbps
        '3': 3,  # 3Mbps
        '4': 4,  # 4Mbps
        '5': 5   # 5Mbps
    }

    SET_RESOLUTION = (
        "high"  # 720p
        "low"   # 480p
    )

    DISTANCE_RANGE = ( # in centimeters
        20,     # lower value
        500,    # higher value
    )

    ANGLE_RANGE = ( # in degrees
        0,     # lower value
        360,    # higher value
    )

    FLIP_DIRECTION = {
        "left": "l",
        "right": "r",
        "forward": "f",
        "backward": "b"
    }

    COORDINATES_RANGE = (
        -500,
        500
    )

    def __init__(self, tello_ip=TELLO_IP, retry_count=RETRY_COUNT):
        """
        Tello object initialization

        :param tello_ip: Tello Drone IP
        :type tello_ip: str

        :param retry_count: Number of retries after a failed command
        :type retry_count: int
        """

        global threads_initialized, drones, client_socket

        self.address = (tello_ip, self.TELLO_PORT)
        self.retry_count = retry_count

        # Save current time
        self.last_received_command_timestamp = time.time()
        self.last_rc_control_timestamp = time.time()

        if not threads_initialized:

            # socket for sending cmd
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            client_socket.bind((self.LOCAL_IP, self.TELLO_PORT))

            # __receive_thread callback for responses
            self.cmd_receive_thread = Thread(target=self.__receive_thread)
            self.cmd_receive_thread.daemon = True
            self.cmd_receive_thread.start()

            threads_initialized = True

        drones[tello_ip] = {'responses': [], 'state': {}}
        self.LOGGER.info(f"Tello instance was initialized. tello_ip: '{tello_ip}'. Port: '{self.TELLO_PORT}'.")


    def __send_command_and_return(self, command: str, timeout: int = TIMEOUT):
        """
        Sends "Control Commands" to the Tello and waits for response.

        If self.command_timeout is exceeded before a response is received,
        a RuntimeError exception is raised.
        
        :param command: Command to send.
        :type command: str

        :param timeout: maximum waiting time in seconds to get response
        :type timeout: int
        
        :return (str): response from Tello
        
        :raise Exception: If no response is received within self.timeout seconds.

        """

        global client_socket

        diff = time.time() - self.last_received_command_timestamp
        
        if diff < self.TIME_BTW_COMMANDS:
            self.LOGGER.debug(f'Waiting {diff} seconds to execute command: {command}...')
            time.sleep(diff)

        self.LOGGER.debug(f"Send command: '{command}'")
        timestamp = time.time()

        client_socket.sendto(command.encode('utf-8'), self.address)
        
        responses = self.__get_own_udp_object()['responses']
 
        while not responses:
            # ToDo Check responses
            if time.time() - timestamp > timeout:
                message = f"Aborting command '{command}'. Did not receive a response after {timeout} seconds"
                self.LOGGER.warning(message)
                return message
            time.sleep(0.1)

        self.last_received_command_timestamp = time.time()

        first_response = responses.pop(0)  # first datum from socket

        try:
            response = first_response.decode("utf-8")
        except UnicodeDecodeError as e:
            self.LOGGER.error(e)
            return "response decode error"
        
        response = response.rstrip("\r\n")

        self.LOGGER.debug(f"Response {command}: '{response}'")
        return response

    def __get_own_udp_object(self):
        """Get own object from the global drones dict. 
        
        This object is filled with responses and state information by the receiver threads.
        """
        global drones

        tello_ip = self.address[0]
        return drones[tello_ip]

    def send_control_command(self, command: str, timeout: int = TIMEOUT) -> bool:
        """Send control command to Tello and wait for its response.
        """
        response = "max retries exceeded"
        for i in range(0, self.retry_count):
            response = self.__send_command_and_return(command, timeout=timeout)

            if 'ok' in response.lower():
                return True

            self.LOGGER.debug(f"Command attempt #{i} failed for command: '{command}'")

        self.LOGGER.error(f"Command '{command}' failed")
        return False

    def connect(self):
        """Connect and enter SDK mode
        """

        self.LOGGER.debug('Initiate SDK mode')
        response = self.send_control_command("command")

        if response == True:
            self.sdk_mode_enable = True
            self.LOGGER.info('SDK mode successfully started')

            # Get SDK version
            self.sdk_version = self.get_sdk_version()
            self.LOGGER.info(f'SDK version: {self.sdk_version}')

            # Get hardware type
            self.hardware = self.get_hardware()
            self.LOGGER.info(f'Hardware: {self.hardware}')

            # Get battery percentage
            battery = self.get_battery()
            self.LOGGER.info(f'Battery percentage: {battery}')

            # Init State server thread
            # _state_thread callback for read Tello State
            self.state_receiver_thread = Thread(target=self.__state_thread)
            self.state_receiver_thread.daemon = True
            self.state_receiver_thread.start()
        else:
            self.LOGGER.error('Fail to enter in SDK mode. Try again')

        # if wait_for_state:
        #     REPS = 20
        #     for i in range(REPS):
        #         if self.__get_current_state():
        #             t = i / REPS  # in seconds
        #             self.LOGGER.debug(f"'.connect()' received first state packet after {t} seconds")
        #             break
        #         time.sleep(1 / REPS)

        #     if not self.__get_current_state():
        #         self.LOGGER.warning('Did not receive a state packet from the Tello')

    # ToDo Update state
    def __get_current_state(self) -> dict:
        """Call this function to obtain the state of the Tello Drone. 
        
        :return (dict): Dictorionary with all Tello State fields.
        """
        return self.__get_own_udp_object()['state']

    def __receive_thread(self):
        """UDP response receiver.

        Used to receive response from the UDP server and not block the main thread
        """

        while True:
            try:
                response, address = client_socket.recvfrom(1024)

                address = address[0]
                self.LOGGER.debug(f'Received from {address}: {response}')

                if address not in drones:
                    continue

                drones[address]['responses'].append(response)

            except Exception as e:
                self.LOGGER.error(e)
                break

    def __state_thread(self):
        """Tello State UDP receiver

        Listens Tello State information
        """

        state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        state_socket.bind((self.LOCAL_IP, self.STATE_UDP_PORT))

        self.LOGGER.debug('State socket up')

        while True:
            try:
                #if self.client_socket_up == True:
                response, address = state_socket.recvfrom(1024)

                address = address[0]
                self.LOGGER.debug(f'Data received from {address} at state socket')

                if address not in drones:
                    continue

                response = response.decode('ASCII')
                drones[address]['state'] = self.__state_parse(response)

            except Exception as e:
                self.LOGGER.error(e)
                break
            time.sleep(0.2)

    def __state_parse(state: str) -> Dict[str, Union[int, float, str]]:
        """Parse a state line to a dictionary

        Raw Data String format from Tello State:
            “pitch:%d;roll:%d;yaw:%d;vgx:%d;vgy%d;vgz:%d;templ:%d;temph:%d;tof:%d;h:%d;bat:%d;baro:%.2f; time:%d;agx:%.2f;agy:%.2f;agz:%.2f;\r\n”
        """

        # clean up spaces and \r\n
        state = state.strip()
        self.LOGGER.debug(f'Raw state data: {state}')

        if state == 'ok':
            return {}

        state_dict = {}
        for field in state.split(';'):
            split = field.split(':')
            if len(split) < 2:
                continue

            key = split[0]
            value: Union[int, float, str] = split[1]

            if key in self.state_field_converters:
                num_type = self.state_field_converters[key]
                try:
                    value = num_type(value)
                except ValueError as e:
                    self.LOGGER.error(f'Error parsing state value for {key}: {value} to {num_type}')
                    self.LOGGER.error(e)
                    continue

            state_dict[key] = value

        return state_dict

    def __check_sdk_mode(self):
        """Check if the drone is set in SDK mode
        """

        if self.sdk_mode_enable:
            pass
        else:
            message = f'Enable SDK mode with connect() function.'
            self.LOGGER.error(message)
            raise ValueError(message)

    def __check_sdk_version(self, version):
        """Check sdk version base on given version
        """

        if self.sdk_version == version:
            pass
        else:
            message = f'Unsupported function for the current SDK version {self.sdk_version}'
            self.LOGGER.error(message)
            raise ValueError(message)

    def __check_hardware(self, hardware):
        """Check hardware type
        """

        if self.hardware == hardware:
            pass
        else:
            message = f'Unsupported hardware: "{self.hardware}"'
            self.LOGGER.error(message)
            raise ValueError(message)

    def __convertion_fail(self, field='field', data_type='data type'):
        """Log convertion error
        """

        self.LOGGER.error(f'Failure to convert {field} value to {data_type}')

    def __read_command_fail(self, field='field'):
        """Log read command fail
        """

        self.LOGGER.error(f'Failure to get {field}')

    def __set_command_fail(self, field='field'):
        """Log set command fail
        """

        self.LOGGER.error(f'Failure to set {field}')

    def __control_command_fail(self, field='field'):
        """Log control command fail
        """

        self.LOGGER.error(f'Failure to send control command {field}')

    def get_speed(self):
        """
        Obtain set speed (cm/s) (This is not the current speed)

        :return (float): speed (cm/s) in a range from 10 to 100
        """

        field = "speed"
        data_type = "float"

        try:
            self.__check_sdk_mode()
            speed = self.__send_command_and_return('speed?')

            try:
                speed = float(speed)
                return speed
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)
    
    def get_battery(self):
        """
        Obtain current battery percentage

        :return (int): battery percentage in a range from 0 to 100
        """

        field = "battery"
        data_type = "int"

        try:
            self.__check_sdk_mode()
            battery = self.__send_command_and_return('battery?')

            try:
                battery = int(battery)
                return battery
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)

    def get_flight_time(self):
        """
        Obtain current flight time

        :return (int): flight time in seconds elapsed
        """

        field = "time"
        data_type = "int"

        try:
            self.__check_sdk_mode()
            time = self.__send_command_and_return('time?')

            try:
                # remove 's' from string response
                time = time.replace('s', '')
                time = int(time)
                return time
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)

    def get_wifi_snr(self):
        """
        Obtain Wi-Fi SNR (Signal to Noise Ratio)

        :return (int): wifi SNR            
        """

        field = "Wi-Fi SNR"
        data_type = "str"

        try:
            self.__check_sdk_mode()
            wifi = self.__send_command_and_return('wifi?')

            try:
                wifi = str(wifi)
                return wifi
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)

    def get_sdk_version(self):
        """
        Obtain the Tello SDK version

        :return (int): sdk version.
        
        SDK version can be 20 for 2.0 or 30 for 3.0
        """

        field = "SDK version"
        data_type = "int"

        try:
            self.__check_sdk_mode()
            sdk = self.__send_command_and_return('sdk?')

            try:
                sdk = int(sdk)
                return sdk
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)

    def get_serial(self):
        """
        Obtain Tello serial number

        :return (str): serial number.
        """

        field = "serial number"
        data_type = "str"

        try:
            self.__check_sdk_mode()
            serial = self.__send_command_and_return('sn?')

            try:
                serial = str(serial)
                return serial
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)
    
    def get_hardware(self):
        """
        Get hardware type.

        `'TELLO'` or `'RMTT'` (Robomaster TT)

        :return (str): hardware.
        """

        field = "hardware"
        data_type = "str"

        try:
            self.__check_sdk_mode()
            self.__check_sdk_version(30)

            hardware = self.__send_command_and_return('hardware?')
            
            try:
                hardware = str(hardware)
                return hardware
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)

    def get_wifi_version(self):
        """
        Get Wi-Fi version.

        Query the -WiFi version of the open-source controller. (Only applies to 'Robomaster TT')

        :return (str): wifi version.
        """

        field = "wifi version"
        data_type = "str"

        try:
            self.__check_sdk_mode()
            self.__check_hardware('RMTT')

            wifi_version = self.__send_command_and_return('wifiversion?')
            
            try:
                wifi_version = str(wifi_version)
                return wifi_version
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)
    
    def get_ap(self):
        """
        Get the name and password of the current router to be connected. (Only applies to 'Robomaster TT')

        :return (str): name and password.
        """

        field = "name and password"
        data_type = "str"

        try:
            self.__check_sdk_mode()
            self.__check_hardware('RMTT')

            ap = self.__send_command_and_return('ap?')
            
            try:
                ap = str(ap)
                return ap
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)

    def get_ssid(self):
        """
        Get the current SSID of the drone

        :return (str): SSID.
        """

        field = "SSID"
        data_type = "str"

        try:
            self.__check_sdk_mode()
            self.__check_hardware('RMTT')

            ssid = self.__send_command_and_return('ssid?')
            
            try:
                ssid = str(ssid)
                return ssid
            except:
                self.__convertion_fail(field, data_type)
                return -1
        except:
            self.__read_command_fail(field)
    
    def set_speed(self, speed=SET_SPEED["mid"]):
        """Set the current speed (cm/s) in range from 10 to 100

        :param speed: speed in cm/s
        :type speed: float
        """

        field = 'speed'

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(speed, self.SPEED_RANGE):
                self.__send_command_and_return(f'speed {speed}')
            else:
                self.__value_out_range(self.SPEED_RANGE)
        except:
            self.__set_command_fail(field)

    def set_wifi(self, ssid, password):
        """Set Wi-Fi name (SSID) and password

        :param ssid: Wi-Fi name
        :type speed: str

        :param password: Wi-Fi password
        :type password: str
        """

        field = 'SSID and password'

        try:
            self.__check_sdk_mode()
            ssid = ssid.replace(' ', '-')
            self.__send_command_and_return(f'wifi {ssid} {password}')
        except:
            self.__set_command_fail(field)

    def set_mission_on(self):
        """Enable mission pad detection (forward and downward)
        """

        field = 'mon'

        try:
            self.__check_sdk_mode()
            self.__send_command_and_return(f'mon')
            self.mission_mode_enable = True
        except:
            self.__set_command_fail(field)
    
    def set_mission_off(self):
        """Disable mission pad detection
        """

        field = 'moff'

        try:
            self.__check_sdk_mode()
            self.__send_command_and_return(f'moff')
            self.mission_mode_enable = False
        except:
            self.__set_command_fail(field)

    def set_mission_detection(self, direction):
        """Set detection direction on mission mode enable

        The detection frequency is 20 Hz if only the forward or
        downward detection is enable. If both, forward and downward
        detection are enable, the detection frequency is 10 Hz.

        :param direction: set direction of detection
        :type direction: str
        """

        options = """
        Options:
            'downward' - Enable downward detection only
            'forward'  - Enable forward detection only
            'both'     - Enable both, forward and downward detection"""

        field = 'mdirection'

        try:
            self.__check_sdk_mode()

            if direction in self.MISSION_DETECTION_DIRECTION:
                if self.mission_mode_enable:
                    self.__send_command_and_return(f'mdirection {self.MISSION_DETECTION_DIRECTION[direction]}')
                else:
                    self.LOGGER.error("Perform set_mission_on() before set this command")
            else:
                self.__invalid_option(options)
        except:
            self.__set_command_fail(field)

    def set_ap(self, ssid, password):
        """Set the Tello to station mode, and connect to a
        new acces point with the access point's ssid and password

        :param ssid: Access point name
        :type ssid: str

        :param password: Access point password
        :type password: str
        """

        field = 'ap'

        try:
            self.__check_sdk_mode()
            self.__send_command_and_return(f'app {ssid} {password}')
        except:
            self.__set_command_fail(field)

    def set_wifi_channel(self, channel):
        """Set the Wi-Fi channel of the open-source controller
        This function only applies to the open-source controller

        :param channel: channel to be set
        :type channel: str
        """

        field = 'Wi-Fi channel'

        try:
            self.__check_sdk_mode()
            self.__check_hardware('RMTT')
            self.__send_command_and_return(f'wifisetchannel {channel}')
        except:
            self.__set_command_fail(field)

    def set_video_port(self, info, video):
        """Set the ports for pushing status information and video streams.

        The range of ports is 1025 to 65535

        :param info: port for pushing status information
        :type info: str

        :param video: port for pushing video information
        :type vedio: str
        """

        field = 'ports settings'

        try:
            self.__check_sdk_mode()
            self.__check_sdk_version(30)
            self.__send_command_and_return(f'port {info} {video}')
        except:
            self.__set_command_fail(field)

    def set_fps(self, fps=SET_FPS[0]):
        """Set video stream frame rate.

        :param fps: Frames per second (Default high)
        :type fps: str
        """

        options = """
        Options:    
            "high"    - indicating 30fps (default)
            "middle"  - indicating 15ps
            "low"     - indicating 5fps"""

        field = 'fps'

        try:
            self.__check_sdk_mode()
            self.__check_sdk_version(30)

            if fps in self.SET_FPS:
                self.__send_command_and_return(f'setfps {fps}')
            else:
                self.__invalid_option(options)
        except:
            self.__set_command_fail(field)

    def set_bitrate(self, bitrate=SET_BITRATE['auto']):
        """Set the video stream bit rate.

        :param bitrate: bitrate parameter
        :type bitrate: int
        """

        options = """
        Options:    
            'auto' - auto
            '1' - 1Mbps
            '2' - 2Mbps
            '3' - 3Mbps
            '4' - 4Mbps
            '5' - 5Mbps"""

        field = 'bitrate'

        try:
            self.__check_sdk_mode()
            self.__check_sdk_version(30)
            bitrate = str(bitrate)
            if bitrate in self.SET_BITRATE:
                self.__send_command_and_return(f'setbitrate {self.SET_BITRATE[bitrate]}')
            else:
                self.__invalid_option(options)
        except:
            self.__set_command_fail(field)

    def set_resolution(self, resolution=SET_RESOLUTION[0]):
        """Set the video stream resolution.

        The resolution parameter specifies the resolution, whose value
        can be "high" or "low", indicating 720P and 480P, respectively.
        """

        options = """
        Options:    
            "high" - 720p
            "low"  - 480p"""

        field = 'resolution'

        try:
            self.__check_sdk_mode()
            self.__check_sdk_version(30)

            if resolution in self.SET_RESOLUTION:
                self.__send_command_and_return(f'setresolution {resolution}')
            else:
                self.__invalid_option(options)
        except:
            self.__set_command_fail(field)

    def takeoff(self):
        """Auto takeoff
        """

        field = "takeoff"

        try:
            self.__check_sdk_mode()
            self.__send_command_and_return(f'takeoff')
        except:
            self.__control_command_fail(field)

    def land(self):
        """Auto landing
        """

        field = "land"

        try:
            self.__check_sdk_mode()
            self.__send_command_and_return(f'land')
        except:
            self.__control_command_fail(field)

    def stream_on(self):
        """Enables video stream
        """

        field = "stream on"

        try:
            self.__check_sdk_mode()
            response = self.__send_command_and_return(f'streamon')
            if response:
                self.LOGGER.info('Video stream enabled')
        except:
            self.__control_command_fail(field)

    def stream_off(self):
        """Disables video stream
        """

        field = "stream off"

        try:
            self.__check_sdk_mode()
            response = self.__send_command_and_return(f'streamoff')
            if response:
                self.LOGGER.info('Video stream disabled')
        except:
            self.__control_command_fail(field)

    def emergency(self):
        """Stop Motors immediately
        """

        field = "emergency"

        try:
            self.__check_sdk_mode()
            response = self.__send_command_and_return(f'emergency')
        except:
            self.__control_command_fail(field)

    def __value_out_range(self, range, value_name=''):
        """Logs out of range message
        """
        msg = f'Range from {range[0]} to {range[1]}'
        if value_name == '':
            self.LOGGER.error(f'Value out of range. {msg}')
        else:
            self.LOGGER.error(f'Value "{value_name}" out of range. {msg}')

    def __invalid_option(self, options):
        """Logs options
        """
        self.LOGGER.error(f'Invalid parameter. {options}')
    
    def __check_in_range(self, value, range):
        """Check if value is on range

        :param value: value to check
        :param range: list values (range)
        """
        if value >= range[0] and value <= range[1]:
            return True
        else:
            return False

    def move_up(self, distance):
        """Ascend given distance in centimeters
        """

        field = "move up"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.DISTANCE_RANGE):
                response = self.__send_command_and_return(f'up {distance}')
            else:
                self.__value_out_range(self.DISTANCE_RANGE)
        except:
            self.__control_command_fail(field)

    def move_down(self, distance):
        """Descend given distance in centimeters
        """

        field = "move down"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.DISTANCE_RANGE):
                response = self.__send_command_and_return(f'down {distance}')
            else:
                self.__value_out_range(self.DISTANCE_RANGE)
        except:
            self.__control_command_fail(field)
    
    def move_left(self, distance):
        """Fly left given distance in centimeters
        """

        field = "move left"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.DISTANCE_RANGE):
                response = self.__send_command_and_return(f'left {distance}')
            else:
                self.__value_out_range(self.DISTANCE_RANGE)
        except:
            self.__control_command_fail(field)

    def move_right(self, distance):
        """Fly right given distance in centimeters
        """

        field = "move right"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.DISTANCE_RANGE):
                response = self.__send_command_and_return(f'right {distance}')
            else:
                self.__value_out_range(self.DISTANCE_RANGE)
        except:
            self.__control_command_fail(field)
    
    def move_forward(self, distance):
        """Moves forward given distance in centimeters
        """

        field = "move forward"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.DISTANCE_RANGE):
                response = self.__send_command_and_return(f'forward {distance}')
            else:
                self.__value_out_range(self.DISTANCE_RANGE)
        except:
            self.__control_command_fail(field)
    
    def move_backward(self, distance):
        """Moves backward given distance in centimeters
        """

        field = "move backward"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.DISTANCE_RANGE):
                response = self.__send_command_and_return(f'back {distance}')
            else:
                self.__value_out_range(self.DISTANCE_RANGE)
        except:
            self.__control_command_fail(field)
    
    def move_clockwise(self, angle):
        """Rotates clockwise given angle in degrees
        """

        field = "rotate clockwise"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.ANGLE_RANGE):
                response = self.__send_command_and_return(f'cw {distance}')
            else:
                self.__value_out_range(self.ANGLE_RANGE)
        except:
            self.__control_command_fail(field)
    
    def move_counterclockwise(self, angle):
        """Rotates counterclockwise given angle in degrees
        """

        field = "rotate counterclockwise"

        try:
            self.__check_sdk_mode()
            if self.__check_in_range(distance, self.ANGLE_RANGE):
                response = self.__send_command_and_return(f'ccw {distance}')
            else:
                self.__value_out_range(self.ANGLE_RANGE)
        except:
            self.__control_command_fail(field)

    def flip(self, direction):
        """Flip given direction
        """

        options = """
        Options:    
            "left"
            "right"
            "forward"
            "backward" """

        field = "flip"

        try:
            self.__check_sdk_mode()
            if direction in self.FLIP_DIRECTION:
                self.__send_command_and_return(f'flip {self.FLIP_DIRECTION[direction]}')
            else:
                self.__invalid_option(options)
        except:
            self.__control_command_fail(field)
    
    def go_to(self, x, y, z, speed):
        """Fly to given coordinates at given speed.

        The coordinates are relative to the current position.
        """

        field = "go to"

        try:
            self.__check_sdk_mode()
            _1 = self.__check_in_range(speed, self.SPEED_RANGE)
            _2 = self.__check_in_range(x, self.COORDINATES_RANGE)
            _3 = self.__check_in_range(y, self.COORDINATES_RANGE)
            _4 = self.__check_in_range(z, self.COORDINATES_RANGE)

            if (_1 and _2 and _3 and _4):
                self.__send_command_and_return(f'go {x} {y} {z} {speed}')
            elif _1 == False:
                self.__value_out_range(self.SPEED_RANGE, 'speed')
            elif (_2 and _3 and _4) == False:
                self.LOGGER.error('Coordinates out of range.')
                self.__value_out_range(self.COORDINATES_RANGE)
        except:
            self.__control_command_fail(field)

    def move_arc(self, x, y, z, ):
        """Hovers in the air
        """

        field = "hover"

        #try:
        #    self.__check_sdk_mode()
        #    self.__send_command_and_return(f'stop')
        #except:
        #    self.__control_command_fail(field)