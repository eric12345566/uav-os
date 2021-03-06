import time

from simple_pid import PID
import numpy as np
import cv2 as cv

# Algo
from module.algo.arucoMarkerDetect import arucoMarkerDetect, arucoMarkerDetectFrame, arucoMarkerSelectDetect

# service
from service.LoggerService import LoggerService

# module
from module.terminalModule import setTerminal
from Loggy import Loggy

# logger = LoggerService()
loggy = Loggy("AlightArucoPIDCtr")


def AlignArucoPIDController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar, terminalService):
    lrPID = PID(0.3, 0.0001, 0.1)
    lrPID.output_limits = (-100, 100)
    fbPID = PID(0.3, 0.0001, 0.1)
    fbPID.output_limits = (-100, 100)
    up_down_velocity = 0
    yaw_velocity = 0
    canLanding = False

    # 降落計時用
    landingStartTime = 0
    LandAlreadyRecord = False

    testMode = False

    # Landing procedure
    while True:
        # Update terminal value
        setTerminal(terminalService, tello)

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

        # ArUco Marker Detect
        corners, haveMarker = arucoMarkerSelectDetect(frame, 0)

        if terminalService.getForceLanding():
            afStateService.forceLanding()
            tello.land()
            break

        if haveMarker:
            # 若有找到降落點，則嘗試進行對準降落

            # 算出中間點位置
            x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
            y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]
            x_centerPixel = x_sum * .25
            y_centerPixel = y_sum * .25
            # logger.afp_debug("x_c: " + str(x_centerPixel) + ",y_c: " + str(y_centerPixel))

            # 讓飛機對準降落點
            # left-right
            lrError = x_centerPixel - frameWidth // 2
            left_right_velocity = lrPID(lrError)
            left_right_velocity = int(left_right_velocity) // 3

            # front-back
            fbError = y_centerPixel - frameHeight // 2
            for_back_velocity = fbPID(fbError)
            for_back_velocity = -int(for_back_velocity) // 3

            # 依照高速進行速度限制
            low_height_max_speed = 20
            if now_height <= 50:
                if left_right_velocity >= low_height_max_speed:
                    left_right_velocity = low_height_max_speed
                elif left_right_velocity <= -low_height_max_speed:
                    left_right_velocity = -low_height_max_speed

                if for_back_velocity >= low_height_max_speed:
                    for_back_velocity = low_height_max_speed
                elif for_back_velocity <= -low_height_max_speed:
                    for_back_velocity = -low_height_max_speed

            # 寫入 frameSharedVar
            frameSharedVar.setLrError(lrError)
            frameSharedVar.setLrPID(left_right_velocity)

            frameSharedVar.setFbError(fbError)
            frameSharedVar.setFbPID(for_back_velocity)

            # 檢查 frame 中心點有沒有在 ArUco Marker 方框內
            rect = np.array(corners)
            rect = rect.reshape([4, 1, 2]).astype(np.int64)
            # loggy.debug("rect: ", rect)

            # 將四個座標往外擴，讓對齊不用那麼準確。
            scaleUpValue = 30
            scaleUpDirArray = [(False, False), (True, False), (True, True), (False, True)]

            rectNew = np.copy(rect)

            for i in range(0, 4):
                firstDir, secondDir = scaleUpDirArray[i]
                # print(rectNew[i][0])
                if firstDir:
                    rectNew[i][0][0] += scaleUpValue
                else:
                    rectNew[i][0][0] -= scaleUpValue

                if secondDir:
                    rectNew[i][0][1] += scaleUpValue
                else:
                    rectNew[i][0][1] -= scaleUpValue

                # 確認不會是負值
                if rectNew[i][0][0] < 0:
                    rectNew[i][0][0] = 0

                if rectNew[i][0][1] < 0:
                    rectNew[i][0][1] = 0

            isFrameCenterInMarker = cv.pointPolygonTest(rectNew, (centerX, centerY), False)

            # 偵測是否可以下降
            # if abs(fbError) < 20 and abs(lrError) < 20:
            #     # canLanding = True
            #     for_back_velocity = 0
            #     left_right_velocity = 0

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
            if LandAlreadyRecord and time.time() - landingStartTime >= 0.5:
                loggy.debug("Time up, Can Landing!")
                LandAlreadyRecord = False
                landingStartTime = 0

                canLanding = True
                for_back_velocity = 0
                left_right_velocity = 0

        else:
            # 否則，回到 FindArucoController 嘗試盲找降落點
            break

        # 將 isFrameCenterInMarker 分享給 FrameWorker
        frameSharedVar.isFrameCenterInMarker = isFrameCenterInMarker

        # In test mode, tello will not fly
        if not testMode:
            if not canLanding:
                tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            else:
                # 已經對準，此controller已經完成
                afStateService.yaw_align()
                break
        else:
            pass
        # 控制辨識幀率


