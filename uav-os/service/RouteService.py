# State
from State.AutoFlightStateEnum import AutoFlightState

from threading import Thread
import time
from Loggy import Loggy

loggy = Loggy("ROUTE")
busStation = {
    64: 'A1',
    109: 'A3'
}

class RouteService( object ):
    def __init__(self, autoFlightStateService, uavSocketService, terminalService):
        self.afStateService = autoFlightStateService
        self.uavSocketService = uavSocketService
        self.terminalService = terminalService

        self.afStateService.waitCommand()

        # Todo:
        '''
            1. 設定邏輯表, 讓 state 跳換符合 prototype
            2. 根據緊急的 command 來做動作 e.g. 一鍵返航、一鍵暫停 ( Enum )
            3. 設定 task list, 讓 route service來控制所有 task 該因應的動作
            4. Set callback 來決定 state 對應的 controller 
        '''
        self.commandFromATC = None
        self.taskInfos = None
        self.taskProgress = 0
        self.progressCount = 0
        self.taskStatus = 'onGoing'

        self.routes = None
        self.routeList = []
        self.getOnBus = False

        self.targetPoint = None

        self.onBusStation = None
        self.offBusStation = None
        self.startPoint = 2
        self.destPoint = None

        self.threading = None

    # Todo: 在啟動 UAVOS 時 或 task type = oneWay 時調用
    def initRoute(self, start_point):
        pass

    # Todo: 從暫停暫停狀態回復時 或 task type = toAndFro 時調用
    def resetRoute(self, start_point, dest_point):
        self.routes = self.uavSocketService.resetRoute( start_point, dest_point)
        return self.routes

    def desideAFState(self):
        # 更新狀態
        self.uavSocketService.updateTaskStatus(self.taskStatus, self.taskProgress)

        if self.afStateService.getState() == AutoFlightState.WAIT_COMMAND:
            '''
                等待從 ATC 拿到 task list 再動作
            '''
            loggy.info( 'waiting for task' )
            self.uavSocketService.initTask()
            while self.taskInfos is None:
                self.taskInfos = self.uavSocketService.getTask()
            self.destPoint = self.taskInfos[ 'destPoint' ]
            self.afStateService.waitRoute()
            pass

        elif self.afStateService.getState() == AutoFlightState.WAIT_ROUTE:
            # Init Route
            while self.routes == None:
                self.routes = self.resetRoute( self.startPoint, self.destPoint )
                time.sleep(0.01)
            # Update route list
            if self.routes['onBus'] == True:
                self.onBusStation = self.routes['getOnStation']
                self.offBusStation = self.routes['getOffStation']

                if self.getOnBus == False:
                    self.routeList = self.routes['getOnRoutes']
                else:
                    self.routeList = self.routes['getOffRoutes']
                self.progressCount = 20 / len( self.routeList )
                self.afStateService.waitBusArrive()
            elif self.routes['onBus'] == False:
                self.routeList = self.routes['routes']
                self.progressCount = 50 / len(self.routeList)
                self.afStateService.readyTakeOff()
            # Init destination
            if len(self.routeList) > 0:
                self.targetPoint = self.routeList.pop(0)

        elif self.afStateService.getState() == AutoFlightState.WAIT_BUS_ARRIVE:
            self.afStateService.readyTakeOff()

        elif self.afStateService.getState() == AutoFlightState.READY_TAKEOFF:
            # 更新 task 完成度
            if self.routes['onBus'] == True:
                self.taskProgress += self.progressCount
            elif self.routes['onBus'] == False:
                self.taskProgress += self.progressCount
            self.afStateService.autoFlight()

        elif self.afStateService.getState() == AutoFlightState.FLYING_MODE:
            # Todo: 若是 routes array.length != 0, 會繼續進到 flying mode
            if len( self.routeList ) > 0:
                self.targetPoint = self.routeList.pop(0)
                self.afStateService.autoFlight()
                # 更新 task 完成度
                if self.routes['onBus'] == True:
                    self.taskProgress += self.progressCount
                elif self.routes['onBus'] == False:
                    self.taskProgress += self.progressCount
            else:
                self.afStateService.finding_aruco()

        elif self.afStateService.getState() == AutoFlightState.FINDING_ARUCO:
            # 此 State 被定義在 Controller 當判斷
            # self.afStateService.yaw_align()
            pass

        elif self.afStateService.getState() == AutoFlightState.YAW_ALIGN:
            self.afStateService.autoLanding()

        elif self.afStateService.getState() == AutoFlightState.AUTO_LANDING:
            self.afStateService.landed()

        elif self.afStateService.getState() == AutoFlightState.LANDED:
            # Todo
            '''
                1. 決定 end 的條件 ( 電量、返家 )
                2. 回到 wait command state ( 根據 task type 決定 )
                3. 回到 wait route state ( 當 task type 是 "toAndFro" 時 )
                4. 回到 wait bus arrive state ( route 還沒結束 ) --> 利用 "某參數" 判斷
            '''
            if not self.getOnBus and self.routes['onBus'] == True:
                self.afStateService.waitRoute()
                self.getOnBus = True

                self.taskProgress = 50
            elif self.getOnBus and self.routes['onBus'] == True:
                self.getOnBus = False
                self.afStateService.end()

                self.taskProgress = 100
            elif self.routes['onBus'] == False:
                self.afStateService.end()

                self.taskProgress = 100
            time.sleep(0.3)

        elif self.afStateService.getState() == AutoFlightState.END:
            if self.taskInfos['type'] == 'oneWay':
                self.taskStatus = 'finish'
                self.startPoint = self.destPoint
                # 更新狀態
                self.uavSocketService.updateTaskStatus(self.taskStatus, self.taskProgress)
                # 清空資訊
                self.taskInfos = None
                self.uavSocketService.clearUavTask()
                self.uavSocketService.clearUavInfos()

            elif self.taskInfos['type'] == 'toAndFro':
                self.taskInfos[ 'destPoint' ] = self.startPoint
                self.startPoint = self.destPoint
                # 將回程設成 oneWay
                self.getOnBus = False
                self.taskInfos['type'] = 'oneWay'

            self.routes = None
            self.routeList = []
            self.taskStatus = 'onGoing'
            self.taskProgress = 0
            self.uavSocketService.clearAllSocketInfos()
            # 回到等待 task
            self.afStateService.waitCommand()

        if self.terminalService.getInfo( 'battery' ) <= 15:
            self.afStateService.powerOff()

    def getOnBusStatus(self):
        return self.getOnBus

    def getOnStation(self):
        return busStation[ self.onBusStation ]

    def getOffStation(self):
        return busStation[ self.offBusStation ]

    def getTargetPoint(self):
        return self.targetPoint

    def getStartPoint(self):
        return self.startPoint

    def getDestPoint(self):
        return self.destPoint

    def setAtcCommand(self, atc_command):
        self.atc_command = atc_command

    def getAtcCommand(self):
        return self.atc_command

    def threadingStart(self):
        self.threading.start()

    # Todo
    '''
        1. 利用 self.killController 來控制各 controller 要不要停止並停止該 Thread
    '''
    def threadingJoin(self):
        self.killController = True
        self.threading.join()
