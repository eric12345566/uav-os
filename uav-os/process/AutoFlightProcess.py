import time
import cv2 as cv
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from service.LoggerService import LoggerService

cmdList = []
logger = LoggerService()


def cmdListAdd(cmd, value):
    cmdList.append({"cmd": cmd, "value": value})


def cmdListClear():
    cmdList.clear()


def cmdUAVRun(FlightCmdService):
    if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
        logger.afp_debug("turn to Input_mode")
        FlightCmdService.registerInputCmdProcess("autoP")
        FlightCmdService.cmdListAssign(cmdList)
        FlightCmdService.startRunCmd()
    if FlightCmdService.currentState() == FlightState.DONE:
        logger.afp_debug("AutoFlight Stop")
        cmdListClear()
        return True


def AutoFlightProcess(uavFrame, OSStateService, FlightCmdService):
    OSStateService.autoFlightInitReady()

    # while OSStateService.getCurrentState() != OSState.READY:
    #     print("wait for OS.ready")

    cmdListAdd(CmdEnum.takeoff, 0)
    cmdListAdd(CmdEnum.move_left, 100)
    cmdListAdd(CmdEnum.move_right, 100)
    cmdListAdd(CmdEnum.land, 0)
    while True:
        if cmdUAVRun(FlightCmdService):
            logger.afp_debug("Done")
            break
