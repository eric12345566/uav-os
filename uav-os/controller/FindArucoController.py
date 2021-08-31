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


def autoSwitchDirection(direction, sleepTime):
    direct = direction
    sTime = sleepTime

    if direction == Direction.start:
        direct = Direction.up
    elif direction == Direction.up:
        sTime = sleepTime + 1
        direct = Direction.right
    elif direction == Direction.right:
        direct = Direction.forward
    elif direction == Direction.forward:
        sTime = sleepTime + 1
        direct = Direction.left
    elif direction == Direction.left:
        direct = Direction.backward
    elif direction == Direction.backward:
        direct = Direction.up
    return direct, sTime


def FindArucoController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService,
                        frameSharedVar, terminalService):
    isSetTimer = False
    timer = AsyncTimer()
    searchDirection = Direction.start
    sleepTime = 0

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
                searchDirection, sleepTime = autoSwitchDirection(searchDirection, sleepTime)
                logger.afp_debug("direction: " + str(searchDirection))

                if searchDirection == Direction.right:
                    timer.setTimer(sleepTime)
                    tello.send_rc_control(20, 0, 0, 0)
                elif searchDirection == Direction.left:
                    timer.setTimer(sleepTime)
                    tello.send_rc_control(-20, 0, 0, 0)
                elif searchDirection == Direction.forward:
                    timer.setTimer(sleepTime)
                    tello.send_rc_control(0, 20, 0, 0)
                elif searchDirection == Direction.backward:
                    timer.setTimer(sleepTime)
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

