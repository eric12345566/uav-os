import numpy as np
import cv2 as cv
import time

# module & algo
from module.algo.arucoMarkerTrack import arucoTrackPostEstimate, arucoMultiTrackPostEstimate
from module.algo.angleBtw2Points import angleBtw2Points
from service.LoggerService import LoggerService
from module.terminalModule import setTerminal

logger = LoggerService()


def arucoMultiPoseCoordinate(telloFrameBFR, matrix_coefficients, distortion_coefficients, frameSharedVar):
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


def arucoIdsFindHelper(ids, requiredId):
    result = np.where(ids == [requiredId])
    # 會回傳一個一維陣列
    return result[0]


def TestMultiArucoYawAlign(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar, terminalService):
    alignComplete = False
    while True:
        # Update terminal value
        setTerminal(terminalService, tello)

        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Get Post Estimation from Aruco Marker
        # 可以一次看多個 Marker 並且輸出多個 Marker 資訊
        centerXList, centerYList, rvecList, tvecList, ids = arucoMultiTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)

        # 偵測是否有沒有看到 Aruco Marker
        if ids is not None and len(ids) >= 2:
            rMarkerIndex = arucoIdsFindHelper(ids, 20)
            mMarkerIndex = arucoIdsFindHelper(ids, 0)
            # logger.afp_debug("Index of id 20: " + str(rMarkerIndex))
            # logger.afp_debug("Index of id 0: " + str(mMarkerIndex))

            # 假設有發現 方向輔助 marker，在執行以下程式
            markList = [(0, 0), (0, 0)]
            if len(rMarkerIndex) > 0 and len(mMarkerIndex) > 0:
                markList[0] = (centerXList[mMarkerIndex[0]], centerYList[mMarkerIndex[0]])
                markList[1] = (centerXList[rMarkerIndex[0]], centerYList[rMarkerIndex[0]])
                rotateAngle = int(angleBtw2Points(markList[0], markList[1]))
                logger.afp_debug("rotateAngle: " + str(rotateAngle))
                yaw_speed = 0
                if 0 <= rotateAngle <= 90 or -86 < rotateAngle < 0:
                    logger.afp_debug("state 1")
                    yaw_speed = 30
                elif 90 < rotateAngle <= 180 or -180 < rotateAngle < -94:
                    logger.afp_debug("state 2")
                    yaw_speed = -30
                elif -94 <= rotateAngle <= -86:
                    logger.afp_debug("state 3")
                    yaw_speed = 0
                    alignComplete = True

                tello.send_rc_control(0, 0, 0, yaw_speed)

        # 如果對準
        if alignComplete:
            logger.afp_debug("yaw align complete")
            break

