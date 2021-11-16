# State
from State.AutoFlightStateEnum import AutoFlightState

from threading import Thread

class RouteService( object ):
    def __init__(self, autoFlightStateService, uavSocketService):
        self.afStateService = autoFlightStateService
        self.uavSocketService = uavSocketService

        # Todo:
        '''
            1. 設定邏輯表, 讓 state 跳換符合 prototype
            2. 根據緊急的 command 來做動作 e.g. 一鍵返航、一鍵暫停 ( Enum )
            3. 設定 task list, 讓 route service來控制所有 task 該因應的動作
            4. Set callback 來決定 state 對應的 controller 
        '''
        self.commandFromATC = None
        self.taskList = []
        self.routes = None

        self.controller = None
        self.threading = None

    def initRoute(self, start_point):
        pass

    def resetRoute(self, start_point, dest_point):
        pass

    def desideAFState(self):
        if self.afStateService.getState() == AutoFlightState.WAIT_COMMAND:
            # Todo
            '''
                等待從 ATC 拿到 test list 再動作
            '''
            self.afStateService.waitRoute()
            pass

        elif self.afStateService.getState() == AutoFlightState.WAIT_ROUTE:
            if( self.route['onBus'] == True ):
                self.afStateService.waitBusArrive()
            elif( self.route['onBus'] == False ):
                self.afStateService.readyTakeOff()

        elif self.afStateService.getState() == AutoFlightState.WAIT_BUS_ARRIVE:
            self.afStateService.readyTakeOff()

        elif self.afStateService.getState() == AutoFlightState.READY_TAKEOFF:
            self.afStateService.autoflight()

        elif self.afStateService.getState() == AutoFlightState.FLYING_MODE:
            self.afStateService.finding_aruco()

        elif self.afStateService.getState() == AutoFlightState.FINDING_ARUCO:
            self.afStateService.yaw_align()

        elif self.afStateService.getState() == AutoFlightState.YAW_ALIGN:
            self.afStateService.autoLanding()

        elif self.afStateService.getState() == AutoFlightState.AUTO_LANDING:
            self.afStateService.landed()

        elif self.afStateService.getState() == AutoFlightState.LANDED:
            # Todo
            '''
                1. 決定 end 的條件 ( 電量、返家 )
                2. 回到 wait command state
                3. 回到 wait route state
                4. 回到 wait bus arrive state ( route 還沒結束 ) --> 利用 "某參數" 判斷
            '''
            pass

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