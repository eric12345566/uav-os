from State.FlightStateEnum import FlightState
import multiprocessing as mp


class FlightCmdService(object):

    def __init__(self):
        self.State = FlightState.INIT_SYSTEM
        self.lock = mp.Lock()
        self.registerProcess = None
        self.cmdList = []

        # Tello Command Run func
        self.UAVCmdRunFunc = None

    """
        utility function
    """
    def __setstate__(self, state):
        self.lock.acquire()
        self.State = state
        self.lock.release()

    def currentState(self):
        return self.State

    """
        State Function
    """
    def initDone(self):
        # 初始化成功，轉換到下一個狀態

        self.__setstate__(FlightState.READY_FOR_CMD)

    def registerCmd(self, processID):
        self.registerProcess = processID

        self.__setstate__(FlightState.INPUT_CMD)

    def cmdListAdd(self, cmd, value):
        self.lock.acquire()
        self.cmdList.append({"cmd": cmd, "value": value})
        self.lock.release()

    def registerUAVCmd(self, uavFunc):
        self.UAVCmdRunFunc = uavFunc

    def startRunCmd(self):
        self.__setstate__(FlightState.RUNNING_CMD)

        # 讓無人機跑 uav
        self.UAVCmdRunFunc(self.cmdList)
