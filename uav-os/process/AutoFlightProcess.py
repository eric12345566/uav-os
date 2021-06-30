import time
import numpy as np
import cv2 as cv
from threading import Thread
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from State.AutoFlightStateEnum import AutoFlightState
from service.LoggerService import LoggerService
from service.AutoFlightStateService import AutoFlightStateService
from module.BackgroundFrameRead import BackgroundFrameRead
from threading import Thread

# Algo
from module.algo.arucoMarkerDetect import arucoMarkerDetect, arucoMarkerDetectFrame
from module.algo.loadCoefficients import load_coefficients
from module.algo.arucoMarkerTrack import arucoTrackWriteFrame


logger = LoggerService()

""" Utilities
"""


def cmdListAdd(cmdList, cmd, value):
    cmdList.append({"cmd": cmd, "value": value})


def cmdListClear(cmdList):
    cmdList.clear()


""" CMD Runner
"""


# TODO: 再多一個是While阻塞式的 CMD List Runner
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
            # logger.afp_debug("CTR READY")
            if FlightCmdService.registerInputCmdProcess("autoP"):
                # logger.afp_debug("register Ctr Process Success")
                pass
            else:
                # logger.afp_debug("register Ctr Process Fail, try again..")
                time.sleep(0.5)
        elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
            FlightCmdService.cmdRunOnce(cmd, value)
            FlightCmdService.startRunCmd()
        elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
            alreadyRunOnce = True
        elif FlightCmdService.currentState() == FlightState.FORCE_LAND:
            # logger.afp_debug("cmd Force Landing")
            break
        elif FlightCmdService.currentState() == FlightState.DONE:
            # logger.afp_debug("CTR DONE")
            if alreadyRunOnce:
                break


def uavGetInfo(infoCmd, FlightCmdService):
    FlightCmdService.runUavInfoCmd(infoCmd)
    while FlightCmdService.currentState() == FlightState.GET_INFO:
        pass
    return FlightCmdService.getUavInfoValue()


def backgroundSendFrame(FrameService, telloFrameBFR, cameraCalibArr):
    """ 使用 Thread 跑此func，將 frame 寫入 FrameService
    """
    while True:
        frame = telloFrameBFR.frame

        # test Add frame
        frame = cv.flip(frame, 1)
        # markedFrame = arucoMarkerDetectFrame(frame)
        markedFrame = arucoTrackWriteFrame(cameraCalibArr[0], cameraCalibArr[1], frame)

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

    # 載入相機校正的參數 (路徑請從UAVCore.py開始算，因為這是從那建立的Process)
    cameraCalibArr = load_coefficients("./module/algo/calibration.yml")
    logger.afp_debug("cameraCalibArr is Load: " + str(cameraCalibArr))

    # 開啟一個 thread，讓他負責傳送frame給FrameProcess顯示
    frameSendWorker = Thread(target=backgroundSendFrame, args=(FrameService, telloFrameBFR, cameraCalibArr,),
                             daemon=True)
    frameSendWorker.start()

    # ------------------ AutoFlightProcess is ready, init code End --------------------
    OSStateService.autoFlightInitReady()
    logger.afp_debug("AutoFlightProcess Start")

    # Wait for OS ready
    while OSStateService.getCurrentState() == OSState.INITIALIZING:
        pass

    """ Main 主程式
    """
    # State
    afStateService = AutoFlightStateService()
    # Global Var

    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        # logger.afp_debug("State: " + str(FlightCmdService.currentState()))

        # Force Landing Handler
        if FlightCmdService.currentState() == FlightState.FORCE_LAND:
            logger.afp_warning("Force Land commit, System Shutdown")
            break

        afStateService.readyTakeOff()
        # TEST_MODE
        # afStateService.testMode()

        # State Controller
        if afStateService.getState() == AutoFlightState.READY_TAKEOFF:
            cmdUavRunOnce(FlightCmdService, CmdEnum.takeoff, 0)
            afStateService.autoLanding()
            pass
        elif afStateService.getState() == AutoFlightState.AUTO_LANDING:
            pass
        elif afStateService.getState() == AutoFlightState.LANDED:
            pass
        elif afStateService.getState() == AutoFlightState.END:
            pass
        elif afStateService.getState() == AutoFlightState.TEST_MODE:
            pass

    logger.afp_info("AutoFlightProcess End")
    # Stop frameSendWorker
    frameSendWorker.join()
