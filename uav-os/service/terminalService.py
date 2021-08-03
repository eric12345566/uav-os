
class terminalService(object):

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

    """
        Utility function
    """
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
        return 0

    def setForceLanding(self, state):
        self.forceLanding = state

    def getForceLanding(self):
        return self.forceLanding