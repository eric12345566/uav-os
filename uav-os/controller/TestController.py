import numpy as np
import cv2 as cv
import time

# module & algo
from module.algo.arucoMarkerTrack import arucoTrackPostEstimate
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


def TestMultiAruco(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar, terminalService):
    while True:
        # Update terminal value
        setTerminal(terminalService, tello)

        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Get Post Estimation from Aruco Marker
        centerX, centerY, rvec, tvec, ids = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)
        frameSharedVar.rvec = rvec
        frameSharedVar.tvec = tvec