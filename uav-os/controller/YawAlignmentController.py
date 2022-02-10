import numpy as np
import cv2 as cv

# module & algo
from module.algo.arucoMarkerTrack import arucoTrackPostEstimate
from service.LoggerService import LoggerService

logger = LoggerService()


def YawAlignmentController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    yaw_speed = 0
    isAlignmentYaw = False
    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Get Post Estimation from Aruco Marker
        centerX, centerY, rvec, tvec, ids = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)
        frameSharedVar.rvec = rvec
        frameSharedVar.tvec = tvec

        if np.all(ids is not None):
            yawError = abs(rvec[0][0][0])

            # 如果相對於 marker 的 yaw 沒那麼準時，進行修正
            if 0.3 <= yawError <= 3.36:
                yaw_speed = 20
                isAlignmentYaw = False
            elif 0 < yawError < 0.3:
                yaw_speed = 0
                isAlignmentYaw = True
            elif 3.36 < yawError < 3.4:
                yaw_speed = 0
                isAlignmentYaw = True
        else:
            yaw_speed = 0

        if not isAlignmentYaw:
            tello.send_rc_control(0, 0, 0, yaw_speed)
        else:
            tello.send_rc_control(0, 0, 0, 0)
            tello.land()
            afStateService.landed()
            break
