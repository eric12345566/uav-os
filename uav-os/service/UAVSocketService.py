import socketio
from Loggy import Loggy

sio = socketio.Client()
loggy = Loggy("UAVSocketService.py")  # The string is the module name what you log from

busInfosObj = None
flight_route = None


def reset_flightRoute():
    flight_route = None
    print('Reset Success')
    print(flight_route)


@sio.event
def connect():
    print("I'm connected!")


@sio.on('busInfos')
def busInfos(busInfos):
    global busInfosObj
    busInfosObj = busInfos


@sio.on('flightRoute_callback')
def flightRoute_callback(route):
    global flight_route
    print('upgrde flightroute')
    flight_route = route


def getFlight_route():
    return flight_route


class UAVSocketService(object):
    def __init__(self):
        # Init socketio client
        self.sio = sio
        self.loggy = loggy

    def runSocket(self):
        self.sio.connect('http://localhost:4000')
        # self.sio.connect('http://192.168.50.89:3000')
        if (self.sio.sid is not None):
            sio.emit('uavConnect', 'Uav-123')

    def emitUavInfos(self, stopBus, busId):
        self.sio.emit('updateUav', {'stopBus': stopBus, 'busId': busId})

    def getBusInfosByLoc(self, loc):
        self.sio.emit('drivingBusInfosByLoc', loc)
        return busInfosObj

    def getBusInfosById(self, busId):
        self.sio.emit('drivingBusInfosById', busId)
        return busInfosObj

    def calculateRoute(self, coordinate):
        self.sio.emit('calculateRoute', {'x': coordinate['x'], 'y': coordinate['y']})
        print('return flightRoute')
        print(str(flight_route))
        # 如果還沒有回傳的話就先卡在這邊不回傳過去AutoFlightProcess
        while flight_route is None:
            self.loggy.info('Route_Calculation Pending')
        return flight_route

    def disconnect(self):
        self.sio.disconnect()
