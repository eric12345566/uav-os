import time

from simple_pid import PID
import numpy as np
import cv2 as cv

# Algo
from module.algo.arucoMarkerDetect import arucoMarkerDetect, arucoMarkerDetectFrame


def autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger):
    lrPID = PID(0.3, 0.0001, 0.1)
    lrPID.output_limits = (-100, 100)
    fbPID = PID(0.3, 0.0001, 0.1)
    fbPID.output_limits = (-100, 100)
    for_back_velocity = 0
    left_right_velocity = 0
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

        # ArUco Marker Detect
        corners, ids, rejectedImgPoints = arucoMarkerDetect(frame)

        if np.all(ids is not None):
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
            isFrameCenterInMarker = cv.pointPolygonTest(rect, (centerX, centerY), False)

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
                logger.afp_debug("Landing Timer Start")
            elif isFrameCenterInMarker == -1 and LandAlreadyRecord:
                # 如果已經在計時但離開了框框，則取消計時
                landingStartTime = 0
                LandAlreadyRecord = False
                logger.afp_debug("Landing Timer Stop")

            # 如果中心點在方框內達到一定時間，則下降（時間以秒計算）
            if LandAlreadyRecord and time.time() - landingStartTime >= 2:
                logger.afp_debug("Time up, Can Landing!")
                LandAlreadyRecord = False
                landingStartTime = 0

                canLanding = True
                for_back_velocity = 0
                left_right_velocity = 0

        else:
            # 否則，嘗試盲找降落點
            left_right_velocity = 0
            up_down_velocity = 0
            for_back_velocity = 0
            isFrameCenterInMarker = -2
            LandAlreadyRecord = False
            landingStartTime = 0

        # 將 isFrameCenterInMarker 分享給 FrameWorker
        frameSharedVar.isFrameCenterInMarker = isFrameCenterInMarker

        # In test mode, tello will not fly
        if not testMode:
            if not canLanding:
                tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            else:
                tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
                # 已經對準到可以下降的狀況，進行下降
                now_height = tello.get_distance_tof()
                logger.afp_debug("now_height: " + str(now_height))
                frameSharedVar.landHeight = now_height
                move_down_cm = 0

                # 檢查高度來決定下降方式
                if 20 <= now_height <= 30:
                    # 如果高度已經在 20 ~ 30 cm 之間，直接下降
                    tello.land()
                    afStateService.landed()
                    break
                else:
                    # 否則，先降低一點高度
                    if now_height // 2 > 30:
                        move_down_cm = int(now_height - now_height // 2)
                        logger.afp_debug("move_down_cm: " + str(move_down_cm))
                        tello.move_down(move_down_cm)
                    else:
                        move_down_cm = int(now_height - 30)
                        if move_down_cm < 20:
                            tello.land()
                            afStateService.landed()
                            break
                        else:
                            logger.afp_debug("move_down_cm: " + str(move_down_cm))
                            tello.move_down(move_down_cm)

                canLanding = False
        else:
            pass
