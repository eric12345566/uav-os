from State.OSStateEnum import OSState
import multiprocessing as mp


class OSStateService(object):
    def __init__(self):
        self.State = OSState.INITIALIZING
        self.lock = mp.Lock()

        # mode: prod, dev, test
        self.mode = "dev"

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

    def setMode(self, mode):
        self.mode = mode

    def getMode(self):
        return self.mode
