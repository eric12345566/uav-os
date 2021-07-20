import numpy as np
import cv2 as cv
import time

# module & algo
from module.algo.arucoMarkerTrack import arucoTrackPostEstimate
from service.LoggerService import LoggerService

logger = LoggerService()


def TestSpeedFly(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Get Post Estimation from Aruco Marker
        centerX, centerY, rvec, tvec = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)

        if rvec is not None and tvec is not None:
            frameSharedVar.rvec = rvec[0][0]
            frameSharedVar.tvec = tvec[0][0]

            if abs(tvec[0][0][1]) > 0.2:
                tello.move_forward(20)
                tello.land()


def TestSpeedController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService,
                        frameSharedVar):
    isFirstTimeGetY = True
    initY = 0
    endY = 0

    isStartTimer = False
    startTime = 0
    endTime = 0

    tello.move_up(50)
    time.sleep(5)
    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Get Post Estimation from Aruco Marker
        centerX, centerY, rvec, tvec = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)

        if rvec is not None and tvec is not None:
            frameSharedVar.rvec = rvec[0][0]
            frameSharedVar.tvec = tvec[0][0]

            # 第一次啟動取 Y 值
            if isFirstTimeGetY:
                # tello.send_rc_control(0, 0, 0, 0)

                centerX, centerY, rvec, tvec = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients,
                                                                      frame)
                initY = tvec[0][0][1]
                isFirstTimeGetY = False

            # 開始計時
            if not isStartTimer:
                startTime = time.time()

                isStartTimer = True

            tello.send_rc_control(0, 10, 0, 0)

            # 檢查是否正負號相反，相反代表已經跨越中線
            if tvec[0][0][1] * initY <= 0:
                endY = tvec[0][0][1]

                endTime = time.time()

                flyLen = abs(endY - initY)
                speed = flyLen / (endTime - startTime)
                logger.afp_debug("startTime: " + str(startTime))
                logger.afp_debug("initY: " + str(initY))
                logger.afp_debug("EndTime: " + str(endTime))
                logger.afp_debug("endY: " + str(endY))
                logger.afp_debug("speed: " + str(speed))
                tello.send_rc_control(0, 0, 0, 0)
                tello.land()
                afStateService.end()
                break
