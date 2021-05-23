import time
import numpy as np
import cv2 as cv
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from service.LoggerService import LoggerService
from module.BackgroundFrameRead import BackgroundFrameRead

# Algo
from module.algo.arucoMarkerDetect import arucoMarkerDetect, arucoMarkerDetectFrame

logger = LoggerService()

""" Utilities
"""


def cmdListAdd(cmdList, cmd, value):
    cmdList.append({"cmd": cmd, "value": value})


def cmdListClear(cmdList):
    cmdList.clear()


""" CMD Runner
"""


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


""" Process
"""


def AutoFlightProcess(FrameService, OSStateService, FlightCmdService):
    # Wait for Controller Ready, and get the frame
    while not OSStateService.getControllerInitState():
        pass

    # Get Frame from UDP using BackgroundFrameRead class (thread)
    telloUDPAddr = FrameService.getAddress()
    telloFrameBFR = BackgroundFrameRead(telloUDPAddr)
    telloFrameBFR.start()
    frame = telloFrameBFR.frame

    # ------------------ AutoFlightProcess is ready, init code End --------------------
    OSStateService.autoFlightInitReady()

    # Wait for OS ready
    while OSStateService.getCurrentState() == OSState.INITIALIZING:
        pass

    logger.afp_debug("AFP Start")

    while True:
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        markedFrame = arucoMarkerDetectFrame(frame)

        # Send frame to FrameProcess
        FrameService.setFrame(markedFrame)
        FrameService.setFrameReady()
