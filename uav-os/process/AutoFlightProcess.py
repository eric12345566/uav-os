import time
import numpy as np
import cv2 as cv
from threading import Thread
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from service.LoggerService import LoggerService
from module.BackgroundFrameRead import BackgroundFrameRead
from threading import Thread
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
        elif FlightCmdService.currentState() == FlightState.FORCE_LAND:
            logger.afp_debug("cmd Force Landing")
            break
        elif FlightCmdService.currentState() == FlightState.DONE:
            logger.afp_debug("CTR DONE")
            if alreadyRunOnce:
                break


def uavGetInfo(infoCmd, FlightCmdService):
    FlightCmdService.runUavInfoCmd(infoCmd)
    while FlightCmdService.currentState() == FlightState.GET_INFO:
        pass
    return FlightCmdService.getUavInfoValue()


def backgroundSendFrame(FrameService, telloFrameBFR):
    """ 使用 Thread 跑此func，將 frame 寫入 FrameService
    """
    while True:
        frame = telloFrameBFR.frame

        # test Add frame
        frame = cv.flip(frame, 1)
        markedFrame = arucoMarkerDetectFrame(frame)

        # Send frame to FrameProcess
        FrameService.setFrame(frame)
        FrameService.setFrameReady()


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

    # 開啟一個 thread，讓他負責傳送frame給FrameProcess顯示
    frameSendWorker = Thread(target=backgroundSendFrame, args=(FrameService, telloFrameBFR,), daemon=True)
    frameSendWorker.start()

    # ------------------ AutoFlightProcess is ready, init code End --------------------
    OSStateService.autoFlightInitReady()
    logger.afp_debug("AutoFlightProcess Start")

    # Wait for OS ready
    while OSStateService.getCurrentState() == OSState.INITIALIZING:
        pass

    cmdUavRunOnce(FlightCmdService, CmdEnum.takeoff, 0)

    # Main
    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        logger.afp_debug("State: " + str(FlightCmdService.currentState()))
        if FlightCmdService.currentState() == FlightState.FORCE_LAND:
            logger.afp_warning("Force Land commit, System Shutdown")
            break

        corners, ids, rejectedImgPoints = arucoMarkerDetect(frame)

        if np.all(ids is not None):
            # print(_ids)
            x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
            y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]

            x_centerPixel = x_sum * .25
            y_centerPixel = y_sum * .25
        else:
            x_centerPixel = 0.0
            x_centerPixel = 0.0

        # logger.afp_debug("x_c: " + str(x_centerPixel) + ",y_c: " + str(y_centerPixel))

        cmdUavRunOnce(FlightCmdService, CmdEnum.move_forward, 100)
        cmdUavRunOnce(FlightCmdService, CmdEnum.move_back, 100)

    # Stop frameSendWorker
    frameSendWorker.join()
