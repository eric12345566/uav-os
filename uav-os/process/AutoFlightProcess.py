import time

import cv2 as cv
from djitellopy import Tello
from threading import Thread
import keyboard
import time
from Loggy import Loggy
import matplotlib.pyplot as plt

# Controller
from controller.AutoFlightController import autoFlightController
from controller.AutoLandingController import autoLandingController
from controller.AutoLandingSecController import AutoLandingSecController, RvecTest, TestSpeedFly, AdjustDistToTarget, \
    AutoLandingNewSecController
from controller.YawAlignmentController import YawAlignmentController
from controller.AutoLandingThirdController import AutoLandingThirdController
from controller.YawAlignMultiArucoController import YawAlignMultiArucoController
from controller.FindArucoController import FindArucoController
from controller.ArucoPIDLandingController import ArucoPIDLandingController
from controller.terminalController import terminalController
from controller.ArucoPosePIDAlignController import ArucoPosePIDAlignController

# State
from State.OSStateEnum import OSState
from State.AutoFlightStateEnum import AutoFlightState

# Service
from service.LoggerService import LoggerService
from service.AutoFlightStateService import AutoFlightStateService
from service.RouteService import RouteService

# Module
from module.BackgroundFrameRead import BackgroundFrameRead
from module.FrameSharedVar import FrameSharedVar
import process.terminalProcess as tp
from module.IndoorLocationShared import IndoorLocationShared

# Worker
import worker.indoorLocationWorker as iLWorker

# Algo
from module.algo.loadCoefficients import load_coefficients
from module.algo.arucoMarkerTrack import arucoTrackWriteFrame, arucoMultiTrackWriteFrame
from module.algo.arucoMarkerDetect import arucoMarkerDetectFrame
from module.terminalModule import setTerminal
from module.indoorLocationAlgo.QrcodePositionAlgo import streamDecode
from module.algo.angleBtw2Points import angleBtw2Points
import numpy as np

logger = LoggerService()
loggy = Loggy("AFP")


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
        # cv.putText(frame, f"rvec: {frameSharedVar.rvec}", (20, 30),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)
        # cv.putText(frame, f"tvec: {frameSharedVar.tvec}", (20, 70),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)
        # cv.putText(frame, f"ids: {ids}", (20, 110),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)
        # cv.putText(frame, f"RAngle: {RotateAngle}", (20, 150),
        #            cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (0, 255, 0), 2, cv.LINE_AA)

        # For ArucoPosePID
        cv.putText(frame, f"rvec: {frameSharedVar.rvec}", (20, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"tvec: {frameSharedVar.tvec}", (20, 70),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"lrError: {frameSharedVar.lrError}, fbError: {frameSharedVar.fbError}", (20, 110),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"lrPID: {frameSharedVar.lrPID}, fbPID: {frameSharedVar.fbPID}", (20, 150),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"InMarker: {frameSharedVar.isFrameCenterInMarker}, height: {frameSharedVar.landHeight}", (20, 190),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"RAngle: {RotateAngle}", (20, 230),
                   cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2, cv.LINE_AA)

        # Send frame to FrameProcess
        FrameService.setFrame(frame)
        FrameService.setFrameReady()


""" Process
"""


def AutoFlightProcess(FrameService, OSStateService, terminalService, uavSocketService):
    # <Deprecated: 拋棄 Controller Process> Wait for Controller Ready, and get the frame
    # while not OSStateService.getControllerInitState():
    #     pass

    # init Tello object
    tello = Tello()
    tello.connect()

    # Init terminal
    setTerminal(terminalService, tello)
    terminalCtrl = Thread(target=terminalController, args=(terminalService, uavSocketService,), daemon=True)
    terminalCtrl.start()

    # Tello Info
    loggy.info("Battery: ", tello.get_battery())
    loggy.info("temperature: ", tello.get_temperature())

    # stream
    tello.streamoff()
    tello.streamon()

    # Get Frame from UDP using BackgroundFrameRead class (thread)ㄒ
    telloUDPAddr = tello.get_udp_video_address()
    telloFrameBFR = BackgroundFrameRead(telloUDPAddr)
    telloFrameBFR.start()

    # 新增一個可以與 frameSendWorker 快速共享變數的物件
    frameSharedVar = FrameSharedVar()

    # 載入相機校正的參數 (路徑請從UAVCore.py開始算，因為這是從那建立的Process)
    cameraCalibArr = load_coefficients("./module/algo/calibration.yml")
    # logger.afp_debug("cameraCalibArr is Load: " + str(cameraCalibArr))
    loggy.debug("cameraCalibArr is Load: ", cameraCalibArr)

    # 開啟一個 thread，讓他負責傳送frame給FrameProcess顯示
    frameSendWorker = Thread(target=backgroundSendFrame, args=(FrameService, telloFrameBFR, cameraCalibArr,
                                                               frameSharedVar,), daemon=True)
    frameSendWorker.start()

    # ------------------ AutoFlightProcess is ready, init code End --------------------

    OSStateService.autoFlightInitReady()
    # logger.afp_debug("AutoFlightProcess Start")
    loggy.info("AutoFlightProcess Start")

    # Wait for OS ready
    while OSStateService.getCurrentState() == OSState.INITIALIZING:
        pass

    # 室內定位座標 Worker 與 室內定位座標 var 共享物件
    # TODO: 增加 terminalService 進去indoorLocationWorker
    indoorLocationSharedVar = IndoorLocationShared()
    indoorLocationWorker = Thread(target=iLWorker.indoorLocationWorker,
                                  args=(telloFrameBFR, indoorLocationSharedVar, terminalService, tello), daemon=True)
    indoorLocationWorker.start()

    """ State
    """
    afStateService = AutoFlightStateService()
    routeService = RouteService( afStateService, uavSocketService, terminalService )

    onBus = False
    # TODO: 把TestMode
    # TEST_MODE
    # afStateService.testMode()

    # Init busInfos (已知目的點)
    busId = ''

    """ Main 主程式
    """
    while True:
        # Update terminal value
        setTerminal(terminalService, tello)
        if terminalService.getForceLanding() == False and afStateService.getState() == AutoFlightState.FORCE_LANDING:
            afStateService.readyTakeOff()

        if afStateService.getState() == AutoFlightState.WAIT_ROUTE:
            pass
        # Auto Flight State Controller
        # 目前是A0駛往A1會起飛
        # LandingStatus 告訴公車目前狀態 True:可做動作 ; False:不可做動作
        elif afStateService.getState() == AutoFlightState.WAIT_BUS_ARRIVE:
            loggy.info('wait bus arrive')
            onBusStation = routeService.getOnStation()
            offBusStation = routeService.getOffStation()
            busInfos = uavSocketService.getBusInfosByLoc( onBusStation )
            if not routeService.getOnBus:  # 在基地等指令 車子往A1走時
                while busInfos is None:
                    setTerminal(terminalService, tello)
                    busInfos = uavSocketService.getBusInfosByLoc( onBusStation )
                    time.sleep(0.01)
                    pass
                busId = busInfos['busId']
                uavSocketService.emitUavInfos(True, busId, True)
            elif routeService.getOnBus:  # 在車子上等指令 等待車子靠站
                busInfos = uavSocketService.getBusInfosById(busId)
                if busInfos is not None:
                    uavSocketService.emitUavInfos(False, busId, True)
                # 在下車前一站告知要下車
                while busInfos is None or busInfos['loc'] != offBusStation or busInfos['status'] != 'going to':
                    setTerminal(terminalService, tello)
                    busInfos = uavSocketService.getBusInfosById(busId)
                    time.sleep(0.01)
                    pass
                uavSocketService.emitUavInfos(True, busInfos['busId'], True)
                # 等待到站
                while busInfos is None or busInfos['loc'] != offBusStation or busInfos['status'] != 'arrive':
                    setTerminal(terminalService, tello)
                    busInfos = uavSocketService.getBusInfosById( busId )
                    time.sleep(0.01)
                    pass
                uavSocketService.emitUavInfos(False, busInfos['busId'], False)

        elif afStateService.getState() == AutoFlightState.READY_TAKEOFF:
            loggy.info('ready takeoff')
            # Take Off
            tello.takeoff()

        elif afStateService.getState() == AutoFlightState.FLYING_MODE:
            # TODO: Function() -> Use to control the E2E aviation
            filDestination = routeService.getTargetPoint()
            destination = np.array([filDestination['x'], filDestination['y']])
            autoFlightController(tello, afStateService, logger, terminalService, destination)

        elif afStateService.getState() == AutoFlightState.FINDING_ARUCO:
            loggy.debug("State: Finding_aruco")
            FindArucoController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
                                frameSharedVar, terminalService)
            continue

        elif afStateService.getState() == AutoFlightState.YAW_ALIGN:
            loggy.debug("State: yaw_alignment")
            YawAlignMultiArucoController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
                                         frameSharedVar, terminalService)
        elif afStateService.getState() == AutoFlightState.AUTO_LANDING:
            # Landing procedure
            # autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger, terminalService)
            # ArucoPIDLandingController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
            #                           frameSharedVar, terminalService)
            AutoLandingThirdController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1],
                                       frameSharedVar, terminalService)
        elif afStateService.getState() == AutoFlightState.LANDED:
            logger.afp_debug("State: Landed")
            pass

        elif afStateService.getState() == AutoFlightState.END:
            # temperObj = terminalService.getTemper()
            # plt.plot( temperObj['time'], temperObj['temperature'])
            # plt.show()
            logger.afp_info("AFP End")
        elif afStateService.getState() == AutoFlightState.POWER_OFF:
            logger.afp_info("Baterry less than 15, Power Off")
            break
        elif afStateService.getState() == AutoFlightState.TEST_MODE:
            loggy.info("State: Test_Mode")
            # autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger)
            # tello.send_rc_control(0, 0, 0, 0)
            # TestSpeedController(tello, telloFrameBFR, cameraCalibArr[0],
            #                     cameraCalibArr[1], afStateService, frameSharedVar)
            # RvecTest(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService, frameSharedVar,
            #          terminalService)
            # tello.send_rc_control(0, 0, 0, 0)
            # TestMultiArucoYawAlign(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
            #                        frameSharedVar, terminalService)
            # AutoLandingThirdController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
            #                            frameSharedVar, terminalService)

            # FindArucoController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
            #                     frameSharedVar, terminalService)
            # YawAlignMultiArucoController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
            #                              frameSharedVar, terminalService)
            ArucoPosePIDAlignController(tello, telloFrameBFR, cameraCalibArr[0], cameraCalibArr[1], afStateService,
                                        frameSharedVar, terminalService)
            # tello.send_rc_control(0, 0, 0, 0)
        elif afStateService.getState() == AutoFlightState.KEYBOARD_CONTROL:
            while True:

                # Update terminal value
                setTerminal(terminalService, tello)
                print("In State")
                if keyboard.read_key() == "p":
                    tello.move_up(20)
                    print("You pressed p")
                if keyboard.read_key() == "o":
                    print("You pressed o")
                    tello.move_down(20)
                if keyboard.read_key() == "w":
                    print("You pressed w")
                    tello.move_forward(20)
                    print("You pressed s")
                if keyboard.read_key() == "s":
                    tello.move_back(20)
                if keyboard.read_key() == "a":
                    tello.move_left(20)
                    print("You pressed a")
                if keyboard.read_key() == "d":
                    print("You pressed d")
                    tello.move_right(20)
                    print("You pressed l")
                if keyboard.read_key() == "l":
                    tello.rotate_clockwise(30)
                if keyboard.read_key() == "k":
                    print("You pressed k")
                    tello.rotate_counter_clockwise(30)
                if keyboard.read_key() == "c":
                    print("You pressed c")
                    terminalService.setKeyboardTrigger(False)
                    afStateService.testMode()
                    print("SW to Test")
                    break
                if keyboard.read_key() == "z":
                    afStateService.autoFlight()
                    print("You pressed z")
                    print("SW to autoFlight")
                    break

        routeService.desideAFState()
    # logger.afp_info("AutoFlightProcess End")
    logger.afp_info("AutoFlightProcess End")
    loggy.debug("AutoFlightProcess End")

    # Stop indoorLocationWorker
    indoorLocationWorker.join()

    # Stop threading
    frameSendWorker.join()
    terminalCtrl.join()

    #                       _oo0oo_
    #                      o8888888o
    #                      88" . "88
    #                      (| -_- |)
    #                      0\  =  /0
    #                    ___/`---'\___
    #                  .' \\|     |// '.
    #                 / \\|||  :  |||// \
    #                / _||||| -:- |||||- \
    #               |   | \\\  -  /// |   |
    #               | \_|  ''\---/''  |_/ |
    #               \  .-\__  '-'  ___/-. /
    #             ___'. .'  /--.--\  `. .'___
    #          ."" '<  `.___\_<|>_/___.' >' "".
    #         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
    #         \  \ `_.   \_ __\ /__ _/   .-` /  /
    #     =====`-.____`.___ \_____/___.-`___.-'=====
    #                       `=---='
    #
    #
    #     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #               佛祖保佑         永無BUG
