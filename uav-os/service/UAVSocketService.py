import socketio
from Loggy import Loggy

loggy = Loggy("SOCKET")
sio = socketio.Client()

busInfosObj = None
routes = None
taskInfos = None

@sio.event
def connect():
    loggy.info( "I'm connected!" )

@sio.on('busInfos')
def busInfos( busInfos ):
    global busInfosObj
    busInfosObj = busInfos

@sio.on('flightRoute')
def getRoutes( routeResult ):
    global routes
    routes = routeResult
    loggy.debug('routeFromSocket',routeResult)

@sio.on('taskInfos')
def getTask( task ):
    global taskInfos
    taskInfos = task
    loggy.debug( 'taskInfos', task )

class UAVSocketService(object):
    def __init__(self):
        # Init socketio client
        self.sio = sio

    def runSocket(self):
        self.sio.connect('http://140.134.39.52:4000')
        if( self.sio.sid is not None ):
            sio.emit('uavConnect', 'Uav-123')

    def emitUavInfos(self, stopBus, busId, getOnStatus):
        sio.emit('updateUav', {'stopBus': stopBus, 'busId': busId, 'getOnStatus': getOnStatus})

    def getBusInfosByLoc(self, loc):
        self.sio.emit('drivingBusInfosByLoc', loc)
        return busInfosObj

    def getBusInfosById(self, busId):
        self.sio.emit('drivingBusInfosById', busId)
        return busInfosObj

    def initRoute(self, start_point):
        pass

    def resetRoute(self, start_point, dest_point):
        self.sio.emit('resetRoute', {'start': start_point, 'dest': dest_point})
        return routes

    def initTask(self):
        self.sio.emit( 'getTask' )

    def getTask(self):
        return taskInfos

    def updateTaskStatus(self, status, progress):
        self.sio.emit( 'updateTaskStatus', { 'status': status, 'progress': progress } )

    def updateUavBodyCondition(self, battery, location, height ):
        self.sio.emit( 'updateUavBodyCondition', { 'battery': battery, 'location': location, 'height': height } )

    def clearUavTask(self):
        self.sio.emit( 'clearUavTask' )

    def clearUavInfos(self):
        self.sio.emit( 'clearUavInfos' )

    def clearAllSocketInfos(self):
        global busInfosObj
        global routes
        global taskInfos
        busInfosObj = None
        routes = None
        taskInfos = None

    def disconnect(self):
        self.sio.disconnect()
