from State.FlightStateEnum import FlightState
import multiprocessing as mp


class FlightCmdService(object):

    def __init__(self):

        # State
        self.__State = FlightState.INIT_SYSTEM
        self.lock = mp.Lock()
        self.__registerProcess = ""

        # CMD
        self.__cmdList = []
        self.__cmdPopIdx = 0
        self.__cmdListLen = 0

        # Get Info
        self.__uavInfoCmd = None
        self.__uavInfoValue = None
        self.__getInfoReturnFlightState = None

    """
        Utility function
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

    def registerInputCmdProcess(self, processID) -> bool:
        # Process 註冊 Service，切換到 INPUT_CMD 狀態，其他人無法使用
        if self.__registerProcess == "":
            self.__registerProcess = processID
            self.__setstate__(FlightState.INPUT_CMD)
            return True
        else:
            return False

    def cmdListAdd(self, cmd, value):
        # 新增一行 CMD 到 List 中
        self.lock.acquire()
        self.__cmdList.append({"cmd": cmd, "value": value})
        self.lock.release()

    def cmdListAssign(self, cmdList):
        # 直接Assign一個List
        self.__cmdList = cmdList

    def cmdRunOnce(self, cmd, value):
        # 至跑一次，注意這會刪除其他
        self.lock.acquire()
        self.__cmdList.clear()
        self.__cmdList.append({"cmd": cmd, "value": value})
        self.lock.release()

    def controller_GetFullCmdList(self):
        # For Controller: 獲取 cmdList
        return self.__cmdList

    def controller_PopCmd(self):
        # Pop一個cmd並return，注意這邊pop從頭開始，
        if not self.isCmdRunAllComplete():
            cmd = self.__cmdList.pop(0)
            self.__cmdPopIdx += 1
            return cmd
        else:
            return None

    def isCmdRunAllComplete(self):
        if self.__cmdListLen == self.__cmdPopIdx:
            return True
        else:
            return False

    def startRunCmd(self):
        # 開始執行 CMD
        self.__setstate__(FlightState.RUNNING_CMD)
        self.__cmdListLen = len(self.__cmdList)
        self.__cmdPopIdx = 0

    def controller_CmdDone(self):
        # For Controller: cmd 執行完
        self.__setstate__(FlightState.DONE)

    def controller_StateBackToReady(self):
        self.__setstate__(FlightState.READY_FOR_CMD)

        # Clear
        self.__registerProcess = ""
        self.__cmdList.clear()

    """ Get UAV Info
    """
    def runUavInfoCmd(self, cmd):
        self.__uavInfoCmd = cmd
        self.__getInfoReturnFlightState = self.__State
        self.__setstate__(FlightState.GET_INFO)

    def getUavInfoValue(self):
        return self.__uavInfoValue

    def controller_getUavInfoCmd(self):
        return self.__uavInfoCmd

    def controller_getUavInfoDone(self, value):
        self.__uavInfoValue = value
        self.__setstate__(self.__getInfoReturnFlightState)

    """ Force Land 
    """

    def forceLand(self):
        self.__setstate__(FlightState.FORCE_LAND)
        self.__cmdList.clear()
