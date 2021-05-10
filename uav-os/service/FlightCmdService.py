from State.FlightStateEnum import FlightState
import multiprocessing as mp


class FlightCmdService(object):

    def __init__(self):
        self.__State = FlightState.INIT_SYSTEM
        self.lock = mp.Lock()
        self.__registerProcess = None
        self.__cmdList = []

    """
        utility function
    """
    def __setstate__(self, state):
        self.lock.acquire()
        self.__State = state
        self.lock.release()

    def currentState(self):
        return self.__State

    """
        State Function
    """
    def initDone(self):
        # 初始化成功，轉換到下一個狀態

        self.__setstate__(FlightState.READY_FOR_CMD)

    def registerInputCmdProcess(self, processID):
        self.__registerProcess = processID

        self.__setstate__(FlightState.INPUT_CMD)

    def cmdListAdd(self, cmd, value):
        self.lock.acquire()
        self.__cmdList.append({"cmd": cmd, "value": value})
        self.lock.release()

    def cmdListAssign(self, cmdList):
        self.__cmdList = cmdList

    def controller_GetCmdList(self):
        return self.__cmdList

    def startRunCmd(self):
        self.__setstate__(FlightState.RUNNING_CMD)

    def controller_CmdDone(self):
        self.__cmdList.clear()
        self.__setstate__(FlightState.DONE)

    def controller_StateBackToReady(self):
        self.__setstate__(FlightState.READY_FOR_CMD)
