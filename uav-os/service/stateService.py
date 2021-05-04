from State.OSStateEnum import OSState
import multiprocessing as mp


class StateService(object):
    def __init__(self):
        self.State = OSState.INITIALIZING
        self.lock = mp.Lock()

    def setState(self, state):
        self.lock.acquire()
        self.State = state
        self.lock.release()

    def getCurrentState(self):
        return self.State
