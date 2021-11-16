class RouteService( object ):
    def __init__(self, autoFlightService, uavSocketService):
        self.autoFlightService = autoFlightService
        self.uavSocketService = uavSocketService

        # Todo:
        '''
            1. 設定邏輯表, 讓 state 跳換符合 prototype
            2. 根據緊急的 command 來做動作 e.g. 一鍵返航、一鍵暫停 ( Enum )
            3. 設定 task list, 讓 route service來控制所有 task 該因應的動作
        '''
        self.commandFromATC = None
        self.taskList = []


    def initRoute(self, start_point):
        pass

    def resetRoute(self, start_point, dest_point):
        pass

    def desideAFState(self, routes):
        self.route = routes

    def setAtcCommand(self, atc_command):
        self.atc_command = atc_command

    def getAtcCommand(self):
        return self.atc_command