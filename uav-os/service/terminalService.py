import time
class terminalService(object):

    # TODO:串接資料
    def __init__(self):
        # init tello parameter
        self.tello_pitch = 0
        self.tello_roll = 0
        self.tello_yaw = 0
        self.tello_battery = 0
        self.lowest_temperature = 0
        self.highest_temperature = 0
        self.average_temperature = 0
        self.barometer = 0
        # force landing
        self.forceLanding = False
        # Tello Control toggle
        self.keyboardTrigger = False
        self.position_rotate = 0
        self.position_x = 0
        self.position_y = 0
        self.qrPosition = -1
        self.tello_high = 0

        # Plot settings
        self.temper_times = []
        self.battery_times = []
        self.temperatures = []
        self.battery = []
        self.startTime = time.time()
    """
        Utility function
    """

    def setBattery(self):
        nowTime = time.time()
        self.battery.append(self.tello_battery)
        self.battery_times.append(nowTime - self.startTime)

    def setTemper(self):
        nowTime = time.time()
        self.temperatures.append(self.average_temperature)
        self.temper_times.append(nowTime - self.startTime)

    def getBattery(self):
        return { 'battery': self.battery, 'time': self.battery_times }

    def getTemper(self):
        return { 'temperature': self.temperatures, 'time': self.temper_times }

    def setInfo(self, key, value):
        if key == 'pitch':
            self.tello_pitch = value
        elif key == 'roll':
            self.tello_roll = value
        elif key == 'yaw':
            self.tello_yaw = value
        elif key == 'battery':
            self.tello_battery = value
        elif key == 'low_temperature':
            self.lowest_temperature = value
        elif key == 'high_temperature':
            self.highest_temperature = value
        elif key == 'temperature':
            self.average_temperature = value
        elif key == 'barometer':
            self.barometer = value
        elif key == 'rotate':
            self.position_rotate = value
        elif key == 'position_X':
            self.position_x = value
        elif key == 'position_Y':
            self.position_y = value
        elif key == 'qrPosition':
            if value != -1:
                self.qrPosition = value
        elif key == 'high':
            self.tello_high = value

    def getInfo(self, key):
        if key == 'pitch':
            return self.tello_pitch
        elif key == 'roll':
            return self.tello_roll
        elif key == 'yaw':
            return self.tello_yaw
        elif key == 'battery':
            return self.tello_battery
        elif key == 'low_temperature':
            return self.lowest_temperature
        elif key == 'high_temperature':
            return self.highest_temperature
        elif key == 'temperature':
            return self.average_temperature
        elif key == 'barometer':
            return self.barometer
        elif key == 'rotate':
            return self.position_rotate
        elif key == 'position_X':
            return self.position_x
        elif key == 'position_Y':
            return self.position_y
        elif key == 'qrPosition':
            return self.qrPosition
        elif key == 'high':
            return self.tello_high
        return 0

    def setForceLanding(self, state):
        self.forceLanding = state

    def getForceLanding(self):
        return self.forceLanding

    def setKeyboardTrigger(self, state):
        self.keyboardTrigger = state

    def getKeyboardTrigger(self):
        return self.keyboardTrigger
