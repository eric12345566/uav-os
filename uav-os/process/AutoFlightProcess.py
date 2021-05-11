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


def cmdListUavRun(FlightCmdService, cmdList):
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


def cmdUavRunOnce(FlightCmdService, cmd, value):
    alreadyRunOnce = False

    while True:
        if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
            logger.afp_debug("CTR READY")
            if FlightCmdService.registerInputCmdProcess("autoP"):
                logger.afp_debug("register Ctr Process Success")
            else:
                logger.afp_debug("register Ctr Process Fail, try again..")
                time.sleep(0.5)
        elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
            FlightCmdService.cmdRunOnce(cmd, value)
            FlightCmdService.startRunCmd()
        elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
            alreadyRunOnce = True
        elif FlightCmdService.currentState() == FlightState.DONE:
            logger.afp_debug("CTR DONE")
            if alreadyRunOnce:
                break


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
        # if state == "first":
        #     if cmdListUavRun(FlightCmdService, cmdList1):
        #         logger.afp_debug("first Done")
        #         state = "second"
        # elif state == "second":
        #     if cmdListUavRun(FlightCmdService, cmdList2):
        #         logger.afp_debug("second Done")
        #         state = "done"
        # elif state == "done":
        #     logger.afp_debug("all done")
        #     break

        if state == "first":
            cmdUavRunOnce(FlightCmdService, CmdEnum.takeoff, 0)
            logger.afp_debug("1")
            cmdUavRunOnce(FlightCmdService, CmdEnum.move_right, 100)
            logger.afp_debug("first Done")
            state = "second"
        elif state == "second":
            cmdUavRunOnce(FlightCmdService, CmdEnum.move_left, 100)
            logger.afp_debug("3")
            cmdUavRunOnce(FlightCmdService, CmdEnum.move_right, 100)
            logger.afp_debug("4")
            cmdUavRunOnce(FlightCmdService, CmdEnum.move_left, 100)
            logger.afp_debug("5")
            cmdUavRunOnce(FlightCmdService, CmdEnum.move_right, 100)
            logger.afp_debug("second Done")
            state = "done"
        elif state == "done":
            cmdUavRunOnce(FlightCmdService, CmdEnum.land, 100)
            logger.afp_debug("all done")
            break


