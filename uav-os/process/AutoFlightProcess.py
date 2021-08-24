import time

import cv2 as cv
from djitellopy import Tello
from threading import Thread

# Controller
from controller.AutoLandingController import autoLandingController
from controller.AutoLandingSecController import AutoLandingSecController, RvecTest, TestSpeedFly, AdjustDistToTarget, \
    AutoLandingNewSecController
from controller.YawAlignmentController import YawAlignmentController
from controller.AutoLandingThirdController import AutoLandingThirdController
from controller.TestController import TestMultiArucoYawAlign

# State
from State.OSStateEnum import OSState
from State.AutoFlightStateEnum import AutoFlightState

# Service
from service.LoggerService import LoggerService
from service.AutoFlightStateService import AutoFlightStateService

# Module
from module.BackgroundFrameRead import BackgroundFrameRead
from module.FrameSharedVar import FrameSharedVar
import process.terminalProcess as tp

# Algo
from module.algo.loadCoefficients import load_coefficients
from module.algo.arucoMarkerTrack import arucoTrackWriteFrame, arucoMultiTrackWriteFrame
from module.terminalModule import setTerminal
from module.algo.angleBtw2Points import angleBtw2Points

logger = LoggerService()


def backgroundSendFrame(FrameService, telloFrameBFR, cameraCalibArr, frameSharedVar):
    """ 使用 Thread 跑此func，將 frame 寫入 FrameService
    """
    while True:
        frame = telloFrameBFR.frame

        # test Add frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # markedFrame = arucoMarkerDetectFrame(frame)
        # markCenterX, markCenterY = arucoTrackWriteFrame(cameraCalibArr[0], cameraCalibArr[1], frame)
        markCenterX, markCenterY, ids = arucoMultiTrackWriteFrame(cameraCalibArr[0], cameraCalibArr[1], frame)

        # Center point of frame
        centerX = frameWidth // 2
        centerY = frameHeight // 2
        frame_center = (centerX, centerY)
        cv.circle(frame, center=(centerX, centerY), radius=5, color=(0, 0, 255), thickness=-1)

        # Rotate Angel
        RotateAngle = 0

        if (markCenterX is not []) and (markCenterY is not []):
            markList = [(0, 0), (0, 0)]
            if ids is not None and len(ids) >= 2:
                # TODO: 確認是 0 跟 20 再做判斷，目前先不做，因為可能會換 id
                if ids[0][0] == 0 and ids[1][0] == 20:
                    markList[0] = (markCenterX[0], markCenterY[0])
                    markList[1] = (markCenterX[1], markCenterY[1])
                elif ids[0][0] == 20 and ids[1][0] == 0:
                    markList[0] = (markCenterX[1], markCenterY[1])
                    markList[1] = (markCenterX[0], markCenterY[0])

                RotateAngle = angleBtw2Points(markList[0], markList[1])

            cv.arrowedLine(frame, markList[0], markList[1], color=(0, 255, 0), thickness=2)


        # Draw Line from frame center to AruCo center
        # cv.arrowedLine(frame, frame_center, (markCenterX, markCenterY), color=(0, 255, 0), thickness=2)

        # Put some text into frame
        # cv.putText(frame, f"X Error: {frameSharedVar.getLrError()} PID: {frameSharedVar.getLrPID():.2f}", (20, 30),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)
        # cv.putText(frame, f"Y Error: {frameSharedVar.getFbError()} PID: {frameSharedVar.getFbPID():.2f}", (20, 70),
        #            cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
        # cv.putText(frame, f"Now Height: {frameSharedVar.landHeight}", (20, 110),
        #            cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
        # cv.putText(frame, f"isCenterIn: {frameSharedVar.isFrameCenterInMarker}", (20, 150),
        #            cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

        # For ArUco Marker new
        # cv.putText(frame, f"rvec: {frameSharedVar.rvec}", (20, 30),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)
        # cv.putText(frame, f"tvec: {frameSharedVar.tvec}", (20, 70),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)

        # For Angle Test
        cv.putText(frame, f"rvec: {frameSharedVar.rvec}", (20, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"tvec: {frameSharedVar.tvec}", (20, 70),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"ids: {ids}", (20, 110),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"RAngel: {RotateAngle}", (20, 150),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)

        # Send frame to FrameProcess
        FrameService.setFrame(frame)
        FrameService.setFrameReady()


""" Process
"""


def AutoFlightProcess(FrameService, OSStateService, terminalService):
    # <Deprecated: 拋棄 Controller Process> Wait for Controller Ready, and get the frame
    # while not OSStateService.getControllerInitState():
    #     pass

    # init Tello object
    tello = Tello()
    tello.connect()

    # Init terminal value
    setTerminal(terminalService, tello)

    # Tello Info
    logger.ctrp_info("battery: " + str(tello.get_battery()))
    logger.ctrp_info("temperature: " + str(tello.get_temperature()))

    # stream
    tello.streamoff()
    tello.streamon()

    # Get Frame from UDP using BackgroundFrameRead class (thread)
    telloUDPAddr = tello.get_udp_video_address()
    telloFrameBFR = BackgroundFrameRead(telloUDPAddr)
    telloFrameBFR.start()

    # 新增一個可以與 frameSendWorker 快速共享變數的物件
    frameSharedVar = FrameSharedVar()

    # 載入相機校正的參數 (路徑請從UAVCore.py開始算，因為這是從那建立的Process)
    cameraCalibArr = load_coefficients("./module/algo/calibration.yml")
    logger.afp_debug("cameraCalibArr is Load: " + str(cameraCalibArr))

    # 開啟一個 thread，讓他負責傳送frame給FrameProcess顯示
    frameSendWorker = Thread(target=backgroundSendFrame, args=(FrameService, telloFrameBFR, cameraCalibArr,
                                                               frameSharedVar,), daemon=True)
    frameSendWorker.start()

    # ------------------ AutoFlightProcess is ready, init code End --------------------
    OSStateService.autoFlightInitReady()
    logger.afp_debug("AutoFlightProcess Start")

    # Wait for OS ready
    while OSStateService.getCurrentState() == OSState.INITIALIZING:
        pass

    """ State
    """
    afStateService = AutoFlightStateService()

    afStateService.readyTakeOff()
    # TEST_MODE
    # afStateService.testMode()

    """ Main 主程式
    """
    while True:
        # Process frame
        # frame = telloFrameBFR.frame
        # frame = cv.flip(frame, 1)
        # frameHeight, frameWidth, _ = frame.shape

        # Force Landing Handler
        # if FlightCmdService.currentState() == FlightState.FORCE_LAND:
        #     logger.afp_warning("Force Land commit, System Shutdown")
        #     break

        # Update terminal value
        setTerminal(terminalService, tello)
        if terminalService.getForceLanding() == False and afStateService.getState() == AutoFlightState.FORCE_LANDING:
            afStateService.readyTakeOff()

        # Auto Flight State Controller
        if afStateService.getState() == AutoFlightState.READY_TAKEOFF:
            # Take Off
            # cmdUavRunOnce(FlightCmdService, CmdEnum.takeoff, 0)
            tello.takeoff()
            # tello.move_up(20)
            # afStateService.autoLanding()
            afStateService.testMode()
        elif afStateService.getState() == AutoFlightState.AUTO_LANDING:
            # Landing procedure
            autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger, terminalService)
        elif afStateService.getState() == AutoFlightState.LANDED:
            logger.afp_debug("State: Landed")
            afStateService.end()
            pass
        elif afStateService.getState() == AutoFlightState.END:
            pass
        elif afStateService.getState() == AutoFlightState.TEST_MODE:
            # autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger)
            # tello.send_rc_control(0, 0, 0, 0)
            # TestSpeedController(tello, telloFrameBFR, cameraCalibArr[0],
            #                     cameraCalibArr[1], afStateService, frameSharedVar)
            # RvecTest(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService, frameSharedVar)
            # TestMultiArucoYawAlign(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
            #                        frameSharedVar, terminalService)
            AutoLandingThirdController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
                                       frameSharedVar, terminalService)

    logger.afp_info("AutoFlightProcess End")

    # Stop frameSendWorker
    frameSendWorker.join()
