from State.FlightStateEnum import FlightState


class flightCmdService(object):
    def __init__(self):
        self.State = FlightState.INIT_SYSTEM

    def initDone(self):
        '''
        初始化成功，轉換到下一個狀態
        :return:
        '''
        self.State = FlightState.READY
