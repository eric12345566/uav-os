import time

from simple_pid import PID
import numpy as np
import cv2 as cv

# Algo
from module.algo.arucoMarkerTrack import arucoPoseCoordinate

# Plotter
from module.Plotter import Plotter

# module
from Loggy import Loggy

loggy = Loggy("ArucoPosePID")


def ArucoPosePIDAlignController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar, terminalService):
    loggy.debug("In ArucoPosePIDAlignCtr")
    dynamicP = 0.3
    dynamicI = 0.0001
    dynamicD = 0.1
    xErrorLand = 3
    yErrorLand = 3

    # plotter
    # pidPlot = Plotter(400, 200, sample_buffer=200)

    # loggy.debug("pidPlot ready")

    left_right_velocity = 0
    for_back_velocity = 0
    up_down_velocity = 0
    yaw_velocity = 0
    canLanding = False

    # 降落計時用
    landingStartTime = 0
    LandAlreadyRecord = False

    testMode = False

    # Landing procedure
    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Center point of frame
        centerX = frameWidth // 2
        centerY = frameHeight // 2

        # 檢查 Frame 中心點有沒有在 Center
        isFrameCenterInMarker = -2

        # Get Height
        now_height = tello.get_distance_tof()
        # logger.afp_debug("now_height: " + str(now_height))
        frameSharedVar.landHeight = now_height

        if now_height <= 50:
            dynamicP = 0.4
            dynamicI = 0.001
            dynamicD = 0.4

            xErrorLand = 3
            yErrorLand = 3
        else:
            dynamicP = 0.3
            dynamicI = 0.003
            dynamicD = 0.7

            xErrorLand = 5
            yErrorLand = 5

        lrPID = PID(dynamicP, dynamicI, dynamicD)
        lrPID.output_limits = (-100, 100)
        fbPID = PID(dynamicP, dynamicI, dynamicD)
        fbPID.output_limits = (-100, 100)

        # ArUco Marker Detect
        # Get Post Estimation from Aruco Marker
        xError, yError, hError, haveMarker, isMarkerCanUse = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients, distortion_coefficients, frameSharedVar)

        if haveMarker:
            if isMarkerCanUse:
                # 若有找到降落點，則嘗試進行對準降落

                # 讓飛機對準降落點
                # left-right
                lrError = int(xError*10)
                left_right_velocity = lrPID(lrError)
                left_right_velocity = int(left_right_velocity) // 3

                # front-back
                fbError = int(yError*10)
                for_back_velocity = fbPID(fbError)
                for_back_velocity = -int(for_back_velocity) // 3

                # 寫入 frameSharedVar
                frameSharedVar.setLrError(lrError)
                frameSharedVar.setLrPID(left_right_velocity)

                frameSharedVar.setFbError(fbError)
                frameSharedVar.setFbPID(for_back_velocity)

                # Plot 輸出
                # pidPlot.plot(left_right_velocity, label="lrPID")
                # pidPlot.plot(for_back_velocity, label="fbPID")

                # TODO: 檢查是否達到降落條件
                if abs(xError) < xErrorLand and abs(yError) < yErrorLand:
                    isFrameCenterInMarker = 1
                else:
                    isFrameCenterInMarker = -1

                # 若中心點在方框內，飛機降速
                if isFrameCenterInMarker == 1:
                    left_right_velocity = 0
                    for_back_velocity = 0

                # 若中心點在方框內，則開始降落計時
                if isFrameCenterInMarker >= 0 and not LandAlreadyRecord:
                    # 如果在中心點框內且尚未計時過，則開始計時
                    landingStartTime = time.time()
                    LandAlreadyRecord = True
                    loggy.debug("Landing Timer Start")
                elif isFrameCenterInMarker == -1 and LandAlreadyRecord:
                    # 如果已經在計時但離開了框框，則取消計時
                    landingStartTime = 0
                    LandAlreadyRecord = False
                    loggy.debug("Landing Timer Stop")

                # 如果中心點在方框內達到一定時間，則下降（時間以秒計算）
                if LandAlreadyRecord and time.time() - landingStartTime >= 1:
                    loggy.debug("Time up, Can Landing!")
                    LandAlreadyRecord = False
                    landingStartTime = 0

                    canLanding = True
                    for_back_velocity = 0
                    left_right_velocity = 0
            else:
                loggy.debug("tvec爆炸不能用")
        else:
            # 否則，回到 FindArucoController 嘗試盲找降落點
            # TODO: 數秒數，太久就自己回來（PID 好像會自己拉回來）
            loggy.debug("Not seen aruco marker marker")

        # 將 isFrameCenterInMarker 分享給 FrameWorker
        frameSharedVar.isFrameCenterInMarker = isFrameCenterInMarker

        # In test mode, tello will not fly
        if not testMode:
            if not canLanding:
                tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            else:
                # 已經對準，此controller已經完成
                tello.send_rc_control(0, 0, 0, 0)
                time.sleep(0.2)
                canLanding = False

                now_height = tello.get_distance_tof()
                # logger.afp_debug("now_height: " + str(now_height))
                loggy.debug("now_height: ", now_height)

                if 20 <= now_height <= 30:
                    # 如果高度已經在 20 ~ 30 cm 之間，直接下降
                    tello.land()
                    # afStateService.landed()
                    break
                else:
                    if now_height // 2 > 30:
                        move_down_cm = int(now_height - now_height // 2)
                        # logger.afp_debug("move_down_cm: " + str(move_down_cm))
                        loggy.debug("move_down_cm: ", move_down_cm)
                        tello.move_down(move_down_cm)
                    else:
                        move_down_cm = int(now_height - 30)
                        if move_down_cm < 20:
                            tello.land()
                            # afStateService.landed()
                            break
                        else:
                            # logger.afp_debug("move_down_cm: " + str(move_down_cm))
                            loggy.debug("move_down_cm: ", move_down_cm)
                            tello.move_down(move_down_cm)
        else:
            pass
