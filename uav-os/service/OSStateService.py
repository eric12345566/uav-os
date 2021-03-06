from State.OSStateEnum import OSState
import multiprocessing as mp


class OSStateService(object):
    def __init__(self):
        self.State = OSState.INITIALIZING
        self.lock = mp.Lock()

        # mode: prod, dev, test
        self.mode = "dev"

        # Process Init State
        self.__controllerInitReady = False
        self.__frameInitReady = False
        self.__autoFlightInitReady = False

    """
        OS State 
    """
    def setState(self, state):
        """
        直接設定State，目前為了方便才這樣寫，未來將會拋棄
        :param state: OSState Enum 狀態
        :return: void
        """
        self.lock.acquire()
        self.State = state
        self.lock.release()

    def getCurrentState(self) -> OSState:
        """
        取得目前的 OS State
        :return: OSState
        """
        return self.State

    def isOSInitReady(self):
        # Deprecated: 拋棄 Controller Process
        # if self.__controllerInitReady and self.__frameInitReady and self.__autoFlightInitReady:
        #     self.setState(OSState.READY)
        # else:
        #     self.setState(OSState.INITIALIZING)

        if self.__frameInitReady and self.__autoFlightInitReady:
            self.setState(OSState.READY)
        else:
            self.setState(OSState.INITIALIZING)

    def controllerInitReady(self):
        # Deprecated: 拋棄 Controller Process
        self.__controllerInitReady = True
        self.isOSInitReady()

    def getControllerInitState(self):
        # Deprecated: 拋棄 Controller Process
        return self.__controllerInitReady

    def frameInitReady(self):
        self.__frameInitReady = True
        self.isOSInitReady()

    def getFrameInitState(self):
        return self.__frameInitReady

    def autoFlightInitReady(self):
        self.__autoFlightInitReady = True
        self.isOSInitReady()

    def getAutoFlightInitState(self):
        return self.__autoFlightInitReady

    """
        Run Mode 
    """
    def setMode(self, mode):
        self.mode = mode

    def getMode(self):
        return self.mode
