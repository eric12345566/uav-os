import numpy as np
import cv2 as cv
import time
from enum import Enum

# module & algo

from module.algo.arucoMarkerTrack import arucoTrackPostEstimate, arucoMarkerSelectPoseEstimate
from service.LoggerService import LoggerService
from module.terminalModule import setTerminal
from controller.AutoLandingThirdController import arucoPoseCoordinate, flyALittle
from controller.AlignArucoPIDController import AlignArucoPIDController

# helper
from helper.AsyncTimer import AsyncTimer

logger = LoggerService()


class Direction(Enum):
    start = "start"
    up = "up"
    right = "right"
    left = "left"
    forward = "forward"
    backward = "backward"


def autoSwitchDirection(direction):
    if direction == Direction.start:
        return Direction.up
    elif direction == Direction.up:
        return Direction.right
    elif direction == Direction.right:
        return Direction.forward
    elif direction == Direction.forward:
        return Direction.left
    elif direction == Direction.left:
        return Direction.backward
    elif direction == Direction.backward:
        return Direction.start


def FindArucoController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService,
                        frameSharedVar, terminalService):
    isSetTimer = False
    timer = AsyncTimer()
    searchDirection = Direction.start

    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # update terminal
        setTerminal(terminalService, tello)

        # 辨識 marker 數值
        xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                  distortion_coefficients, frameSharedVar)

        if not isSeeMarker:
            # 沒有看到 Aruco Marker，進入搜尋模式
            # 搜尋方法為先上升，如果還是沒找到就走一個正方形，重複此動作
            # 設定 Timer
            if not isSetTimer:
                # 決定搜尋方向
                searchDirection = autoSwitchDirection(searchDirection)
                logger.afp_debug("direction: " + str(searchDirection))

                if searchDirection == Direction.right:
                    timer.setTimer(2)
                    tello.send_rc_control(20, 0, 0, 0)
                elif searchDirection == Direction.left:
                    timer.setTimer(4)
                    tello.send_rc_control(-20, 0, 0, 0)
                elif searchDirection == Direction.forward:
                    timer.setTimer(2)
                    tello.send_rc_control(0, 20, 0, 0)
                elif searchDirection == Direction.backward:
                    timer.setTimer(4)
                    tello.send_rc_control(0, -20, 0, 0)
                elif searchDirection == Direction.up:
                    timer.setTimer(4)
                    tello.send_rc_control(0, 0, 20, 0)

                isSetTimer = True

                timer.startTimer()

            # 如果時間到，就停下tello，重跑迴圈
            if timer.isTimesUp():
                logger.afp_debug("isTimeUp")
                tello.send_rc_control(0, 0, 0, 0)
                time.sleep(1)
                isSetTimer = False

        else:
            AlignArucoPIDController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService,
                                    frameSharedVar, terminalService)

