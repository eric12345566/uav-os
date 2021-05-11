import time
import cv2 as cv
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from service.LoggerService import LoggerService

logger = LoggerService()


def cmdListAdd(cmdList, cmd, value):
    cmdList.append({"cmd": cmd, "value": value})


def cmdListClear(cmdList):
    cmdList.clear()


def cmdUAVRun(FlightCmdService, cmdList):
    if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
        logger.afp_debug("CTR READY")
        if FlightCmdService.registerInputCmdProcess("autoP"):
            logger.afp_debug("register CMD Process")
            FlightCmdService.cmdListAssign(cmdList)
            FlightCmdService.startRunCmd()
    if FlightCmdService.currentState() == FlightState.DONE:
        logger.afp_debug("CTR DONE")
        cmdListClear(cmdList)
        return True


def uavGetInfo(infoCmd, FlightCmdService):
    FlightCmdService.runUavInfoCmd(infoCmd)
    while FlightCmdService.currentState() == FlightState.GET_INFO:
        pass
    return FlightCmdService.getUavInfoValue()


def AutoFlightProcess(uavFrame, OSStateService, FlightCmdService):
    state = "first"

    OSStateService.autoFlightInitReady()

    # while OSStateService.getCurrentState() != OSState.READY:
    #     print("wait for OS.ready")
    cmdList1 = []
    cmdListAdd(cmdList1, CmdEnum.takeoff, 0)
    cmdListAdd(cmdList1, CmdEnum.move_left, 100)
    cmdListAdd(cmdList1, CmdEnum.move_right, 100)

    cmdList2 = []
    cmdListAdd(cmdList2, CmdEnum.move_left, 100)
    cmdListAdd(cmdList2, CmdEnum.move_right, 100)
    cmdListAdd(cmdList2, CmdEnum.move_right, 100)
    cmdListAdd(cmdList2, CmdEnum.move_left, 100)
    cmdListAdd(cmdList2, CmdEnum.land, 0)

    while OSStateService.getCurrentState() == OSState.INITIALIZING:
        pass

    while True:
        logger.afp_debug("Battery: " + str(uavGetInfo(CmdEnum.get_battery, FlightCmdService)))
        if state == "first":
            if cmdUAVRun(FlightCmdService, cmdList1):
                logger.afp_debug("first Done")
                state = "second"
        elif state == "second":
            if cmdUAVRun(FlightCmdService, cmdList2):
                logger.afp_debug("second Done")
                state = "done"
        elif state == "done":
            logger.afp_debug("all done")
            break

