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

    def waitBusArrive(self):
        self.State = AutoFlightState.WAIT_BUS_ARRIVE

    def finding_aruco(self):
        self.State = AutoFlightState.FINDING_ARUCO

    def yaw_align(self):
        self.State = AutoFlightState.YAW_ALIGN

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

    # Wait ATC command
    def waitCommand(self):
        self.State = AutoFlightState.WAIT_COMMAND

    # Wait route from back-end
    def waitRoute(self):
        self.State = AutoFlightState.WAIT_ROUTE

    # Uav-os in power-off mode
    def powerOff(self):
        self.State = AutoFlightState.POWER_OFF
