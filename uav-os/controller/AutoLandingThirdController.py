import numpy as np
import cv2 as cv
import time

# module & algo
from module.algo.arucoMarkerTrack import arucoTrackPostEstimate
from service.LoggerService import LoggerService

logger = LoggerService()


def arucoPoseCoordinate(telloFrameBFR, matrix_coefficients, distortion_coefficients, frameSharedVar):
    # Process frame
    frame = telloFrameBFR.frame
    frame = cv.flip(frame, 1)
    frameHeight, frameWidth, _ = frame.shape

    # Get Post Estimation from Aruco Marker
    centerX, centerY, rvec, tvec, ids = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)
    frameSharedVar.rvec = rvec
    frameSharedVar.tvec = tvec

    if np.all(ids is not None):
        # 有看到 aruco marker
        # 輸出整數值的 Error
        xError = int(tvec[0][0][0] * 100)
        yError = int(tvec[0][0][1] * 100)
        hError = int(tvec[0][0][2] * 100)
        isSeeMarker = True
    else:
        # 沒看到 aruco marker
        xError = 0
        yError = 0
        hError = 0
        isSeeMarker = False

    return xError, yError, hError, isSeeMarker


def flyALittle(tello, direction):
    if direction == "f":
        tello.send_rc_control(0, 20, 0, 0)
    elif direction == "b":
        tello.send_rc_control(0, -20, 0, 0)
    elif direction == "l":
        tello.send_rc_control(-20, 0, 0, 0)
    elif direction == "r":
        tello.send_rc_control(20, 0, 0, 0)
    time.sleep(0.6)
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(3)


def AutoLandingThirdController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    while True:
        # 辨識 marker 數值
        xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                  distortion_coefficients, frameSharedVar)

        if isSeeMarker and abs(xError) <= 200.0 and abs(yError) <= 200.0:
            # 如果有看到標點，而且 tvec 數值沒有爆炸
            if abs(xError) >= 4 or abs(yError) >= 4:
                # 如果標點大於可降落範圍，則進行修正到位置
                # 先調整前後
                fbIsOk = False
                while not fbIsOk:
                    # 調整迴圈，讓他調整到適合的位置
                    xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                              distortion_coefficients, frameSharedVar)

                    if isSeeMarker and abs(xError) <= 200 and abs(yError) <= 200:
                        if yError >= 4:
                            # 當飛機在 Aruco Marker 下面（銀色夾子在上）
                            flyALittle(tello, "f")
                        elif yError <= -4:
                            # 當飛機在 Aruco Marker 上面（銀色夾子在上）
                            flyALittle(tello, "b")
                        else:
                            fbIsOk = True

                # 再調整左右
                lrIsOk = False
                while not lrIsOk:
                    # 調整迴圈，讓他調整到適合的位置
                    xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                              distortion_coefficients, frameSharedVar)

                    if isSeeMarker and abs(xError) <= 200 and abs(yError) <= 200:
                        if xError >= 4:
                            # 當飛機在 Aruco Marker 的右邊
                            flyALittle(tello, "l")
                        elif xError <= -4:
                            # 當飛機在 Aruco Marker 的左邊
                            flyALittle(tello, "r")
                        else:
                            lrIsOk = True
            else:
                # 已經到降落狀態，執行降落
                tello.send_rc_control(0, 0, 0, 0)
                time.sleep(2)

                now_height = tello.get_distance_tof()
                logger.afp_debug("now_height: " + str(now_height))

                if 20 <= now_height <= 30:
                    # 如果高度已經在 20 ~ 30 cm 之間，直接下降
                    tello.land()
                    afStateService.landed()
                    break
                else:
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
        else:
            # 如果沒看到標點，或者數值爆炸
            logger.afp_info("沒看到標點或數值爆炸")
            tello.send_rc_control(0, 0, 0, 0)
            time.sleep(3)
