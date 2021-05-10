import time
import cv2 as cv
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum

cmdList = []


def cmdListAdd(cmd, value):
    cmdList.append({"cmd": cmd, "value": value})


def cmdListClear():
    cmdList.clear()


def cmdUAVRun(FlightCmdService):
    if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
        print("AUTO: turn to Input_mode")
        FlightCmdService.registerInputCmdProcess("autoP")
        FlightCmdService.cmdListAssign(cmdList)
        FlightCmdService.startRunCmd()
    if FlightCmdService.currentState() == FlightState.DONE:
        print("AutoFlight Stop")
        cmdListClear()
        return True


def AutoFlightProcess(uavFrame, OSStateService, FlightCmdService):
    print("AutoProcess Start")
    OSStateService.autoFlightInitReady()

    # while OSStateService.getCurrentState() != OSState.READY:
    #     print("wait for OS.ready")

    cmdListAdd(CmdEnum.takeoff, 0)
    cmdListAdd(CmdEnum.move_left, 100)
    cmdListAdd(CmdEnum.move_right, 100)
    cmdListAdd(CmdEnum.land, 0)
    while True:
        if cmdUAVRun(FlightCmdService):
            print("AUTo Done")
            break
