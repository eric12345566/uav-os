import time


class AsyncTimer:
    def __init__(self):
        self.sleepTime = None
        self.timerStartTime = None
        self.timerEndTime = None

    def setTimer(self, sleepTime):
        self.timerStartTime = None
        self.timerEndTime = None
        self.sleepTime = sleepTime

    def startTimer(self):
        self.timerStartTime = time.time()

    def isTimesUp(self):
        self.timerEndTime = time.time()
        if (self.timerEndTime - self.timerStartTime) <= self.sleepTime:
            return False
        else:
            print("elapsed Time: ", self.timerEndTime - self.timerStartTime)
            return True
