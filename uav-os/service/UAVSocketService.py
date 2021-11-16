import socketio

sio = socketio.Client()

busInfosObj = None

@sio.event
def connect():
    print("I'm connected!")

@sio.on('busInfos')
def busInfos( busInfos ):
    global busInfosObj
    busInfosObj = busInfos

class UAVSocketService(object):
    def __init__(self):
        # Init socketio client
        self.sio = sio

    def runSocket(self):
        self.sio.connect('http://127.0.0.1:4000')
        if( self.sio.sid is not None ):
            sio.emit('uavConnect', 'Uav-123')

    def emitUavInfos(self, stopBus, busId):
        sio.emit('updateUav', {'stopBus': stopBus, 'busId': busId})

    def getBusInfosByLoc(self, loc):
        self.sio.emit('drivingBusInfosByLoc', loc)
        return busInfosObj

    def getBusInfosById(self, busId):
        self.sio.emit('drivingBusInfosById', busId)
        return busInfosObj

    def initRoute(self, start_point):
        pass

    def resetRoute(self, start_point, dest_point):
        pass

    def disconnect(self):
        self.sio.disconnect()