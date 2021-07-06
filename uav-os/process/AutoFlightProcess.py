import time
import numpy as np
import cv2 as cv
from simple_pid import PID
from djitellopy import Tello
from threading import Thread

# Controller
from controller.AutoLandingController import autoLandingController

# State
from State.OSStateEnum import OSState
from State.AutoFlightStateEnum import AutoFlightState

# Service
from service.LoggerService import LoggerService
from service.AutoFlightStateService import AutoFlightStateService

# Module
from module.BackgroundFrameRead import BackgroundFrameRead
from module.FrameSharedVar import FrameSharedVar

# Algo
from module.algo.arucoMarkerDetect import arucoMarkerDetect, arucoMarkerDetectFrame
from module.algo.loadCoefficients import load_coefficients
from module.algo.arucoMarkerTrack import arucoTrackWriteFrame

logger = LoggerService()


def backgroundSendFrame(FrameService, telloFrameBFR, cameraCalibArr, frameSharedVar):
    """ 使用 Thread 跑此func，將 frame 寫入 FrameService
    """
    while True:
        frame = telloFrameBFR.frame

        # test Add frame
        frame = cv.flip(frame, 1)
        # markedFrame = arucoMarkerDetectFrame(frame)
        arucoTrackWriteFrame(cameraCalibArr[0], cameraCalibArr[1], frame)

        # Put some text into frame
        cv.putText(frame, f"X Error: {frameSharedVar.getLrError()} PID: {frameSharedVar.getLrPID():.2f}", (20, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"Y Error: {frameSharedVar.getFbError()} PID: {frameSharedVar.getFbPID():.2f}", (20, 70),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
        cv.putText(frame, f"Land Height: {frameSharedVar.landHeight}", (20, 110),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

        # Send frame to FrameProcess
        FrameService.setFrame(frame)
        FrameService.setFrameReady()


""" Process
"""


def AutoFlightProcess(FrameService, OSStateService):
    # <Deprecated: 拋棄 Controller Process> Wait for Controller Ready, and get the frame
    # while not OSStateService.getControllerInitState():
    #     pass

    # init Tello object
    tello = Tello()
    tello.connect()

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

    """ Global Var
    """
    # Auto Landing
    lrPID = PID(0.35, 0.0001, 0.1)
    lrPID.output_limits = (-100, 100)
    fbPID = PID(0.35, 0.0001, 0.1)
    fbPID.output_limits = (-100, 100)
    for_back_velocity = 0
    left_right_velocity = 0
    up_down_velocity = 0
    yaw_velocity = 0
    canLanding = False

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

        # Auto Flight State Controller
        if afStateService.getState() == AutoFlightState.READY_TAKEOFF:
            # Take Off
            # cmdUavRunOnce(FlightCmdService, CmdEnum.takeoff, 0)
            tello.takeoff()
            afStateService.autoLanding()
        elif afStateService.getState() == AutoFlightState.AUTO_LANDING:
            autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger)
            # # Landing procedure
            # # ArUco Marker Detect
            # corners, ids, rejectedImgPoints = arucoMarkerDetect(frame)
            #
            # if np.all(ids is not None):
            #     # 算出中間點位置
            #     x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
            #     y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]
            #     x_centerPixel = x_sum * .25
            #     y_centerPixel = y_sum * .25
            #     # logger.afp_debug("x_c: " + str(x_centerPixel) + ",y_c: " + str(y_centerPixel))
            #
            #     # 讓飛機對準降落點
            #
            #     # left-right
            #     lrError = x_centerPixel - frameWidth // 2
            #     left_right_velocity = lrPID(lrError)
            #     left_right_velocity = int(left_right_velocity) // 3
            #
            #     frameSharedVar.setLrError(lrError)
            #     frameSharedVar.setLrPID(left_right_velocity)
            #
            #     # front-back
            #     fbError = y_centerPixel - frameHeight // 2
            #     for_back_velocity = fbPID(fbError)
            #     for_back_velocity = -int(for_back_velocity) // 3
            #
            #     frameSharedVar.setFbError(fbError)
            #     frameSharedVar.setFbPID(for_back_velocity)
            #
            #     # 偵測是否可以下降
            #     if abs(fbError) < 20 and abs(lrError) < 20:
            #         canLanding = True
            #         for_back_velocity = 0
            #         left_right_velocity = 0
            # else:
            #     left_right_velocity = 0
            #     for_back_velocity = 0
            #
            # if not canLanding:
            #     # cmdUavRunOnce(FlightCmdService, CmdEnum.send_rc_control, [left_right_velocity, for_back_velocity,
            #     #                                                           up_down_velocity, yaw_velocity])
            #     tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            # else:
            #     # cmdUavRunOnce(FlightCmdService, CmdEnum.send_rc_control, [left_right_velocity, for_back_velocity,
            #     #                                                           up_down_velocity, yaw_velocity])
            #     tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            #     # 已經對準到可以下降的狀況，進行下降
            #     # now_height = uavGetInfo(CmdEnum.get_distance_tof, FlightCmdService)
            #     now_height = tello.get_distance_tof()
            #     logger.afp_debug("now_height: " + str(now_height))
            #     frameSharedVar.landHeight = now_height
            #     move_down_cm = 0
            #
            #     # 檢查高度來決定下降方式
            #     if 20 <= now_height <= 30:
            #         # 如果高度已經在 20 ~ 30 cm 之間，直接下降
            #         # cmdUavRunOnce(FlightCmdService, CmdEnum.land, 0)
            #         tello.land()
            #         afStateService.landed()
            #     else:
            #         # 否則，先降低一點高度
            #         if now_height // 2 > 30:
            #             move_down_cm = int(now_height - now_height // 2)
            #             logger.afp_debug("move_down_cm: " + str(move_down_cm))
            #             # cmdUavRunOnce(FlightCmdService, CmdEnum.move_down, move_down_cm)
            #             tello.move_down(move_down_cm)
            #         else:
            #             move_down_cm = int(now_height - 30)
            #             if move_down_cm < 20:
            #                 # cmdUavRunOnce(FlightCmdService, CmdEnum.land, 0)
            #                 tello.land()
            #                 afStateService.landed()
            #             else:
            #                 logger.afp_debug("move_down_cm: " + str(move_down_cm))
            #                 # cmdUavRunOnce(FlightCmdService, CmdEnum.move_down, move_down_cm)
            #                 tello.move_down(move_down_cm)
            #
            #     canLanding = False

        elif afStateService.getState() == AutoFlightState.LANDED:
            logger.afp_debug("State: Landed")
            afStateService.end()
            pass
        elif afStateService.getState() == AutoFlightState.END:
            pass
        elif afStateService.getState() == AutoFlightState.TEST_MODE:
            pass

    logger.afp_info("AutoFlightProcess End")

    # Stop frameSendWorker
    frameSendWorker.join()
