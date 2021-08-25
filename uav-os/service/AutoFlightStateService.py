import time

from State.AutoFlightStateEnum import AutoFlightState


class AutoFlightStateService(object):
    def __init__(self):
        self.State = AutoFlightState.INIT

    # 取得現在的State
    def getState(self):
        return self.State

    # State to TEST_MODE
    def testMode(self):
        self.State = AutoFlightState.TEST_MODE

    # State to READY_TAKEOFF
    def readyTakeOff(self):
        self.State = AutoFlightState.READY_TAKEOFF

    # State to AUTO_LANDING
    def autoLanding(self):
        self.State = AutoFlightState.AUTO_LANDING

    # State to LANDED
    def landed(self):
        self.State = AutoFlightState.LANDED

    # State to END
    def end(self):
        self.State = AutoFlightState.END

    # End 之後回到 ReadyTakeOff
    def backToReady(self):
        self.State = AutoFlightState.READY_TAKEOFF

    # Force Landing
    def forceLanding(self):
        self.State = AutoFlightState.FORCE_LANDING

    # Keyboard Control
    def keyboardControl(self):
        self.State = AutoFlightState.KEYBOARD_CONTROL

    # AutoFlight
    def autoFlight(self):
        self.State = AutoFlightState.FLYING_MODE
