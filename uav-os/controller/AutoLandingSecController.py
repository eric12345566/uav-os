import numpy as np
import cv2 as cv
import time

# module & algo
from module.algo.arucoMarkerTrack import arucoTrackPostEstimate
from module.terminalModule import setTerminal
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


def flyDrtOneSec(tello, direction):
    if direction == "f":
        tello.send_rc_control(0, 20, 0, 0)
    elif direction == "b":
        tello.send_rc_control(0, -20, 0, 0)
    elif direction == "l":
        tello.send_rc_control(-20, 0, 0, 0)
    elif direction == "r":
        tello.send_rc_control(20, 0, 0, 0)
    time.sleep(0.5)
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(3)


def AdjustDistToTargetNew(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    # 先調整前後
    fbIsOk = False
    while not fbIsOk:
        # 調整迴圈，讓他調整到適合的位置
        xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                  distortion_coefficients, frameSharedVar)

        if isSeeMarker and abs(xError) <= 200 and abs(yError) <= 200:
            if 0 <= yError <= 20:
                # 當飛機在 Aruco Marker 下面（銀色夾子在上）
                flyDrtOneSec(tello, "b")
            elif -20 <= yError <= 0:
                # 當飛機在 Aruco Marker 上面（銀色夾子在上）
                flyDrtOneSec(tello, "f")
            else:
                fbIsOk = True

    # 再調整左右
    lrIsOk = False
    while not lrIsOk:
        # 調整迴圈，讓他調整到適合的位置
        xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                  distortion_coefficients, frameSharedVar)

        if isSeeMarker and abs(xError) <= 200 and abs(yError) <= 200:
            if 0 <= xError <= 20:
                # 當飛機在 Aruco Marker 的右邊
                flyDrtOneSec(tello, "r")
            elif -20 <= xError <= 0:
                # 當飛機在 Aruco Marker 的左邊
                flyDrtOneSec(tello, "l")
            else:
                lrIsOk = True


def AutoLandingNewSecController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    while True:
        # 辨識 marker 數值
        xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                  distortion_coefficients, frameSharedVar)

        if isSeeMarker and abs(xError) <= 200.0 and abs(yError) <= 200.0:
            # 若有看到 marker 且數值沒有爆炸
            logger.afp_debug("in 1")
            if abs(xError) >= 20 and abs(yError) >= 20:
                logger.afp_debug("in 2")
                # x, y 的位移都超過 20cm，開始降落程序
                if xError >= 20:
                    tello.move_left(abs(xError))
                elif xError <= -20:
                    tello.move_right(abs(xError))

                if yError >= 20:
                    tello.move_forward(abs(yError))
                elif yError <= -20:
                    tello.move_back(abs(yError))

                tello.land()
                afStateService.end()
                break
            else:
                # 若沒有，進行調整飛行
                logger.afp_debug("in 3")
                AdjustDistToTargetNew(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar)
        else:
            # 沒有到標點或數值爆炸，要另外處理
            logger.afp_debug("not seen arUco Marker or tvec explode")
            tello.send_rc_control(0, 0, 0, 0)
            time.sleep(3)


def AdjustDistToTarget(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    while True:
        # 調整迴圈，讓他調整到適合的位置
        xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                  distortion_coefficients, frameSharedVar)

        if isSeeMarker and abs(xError) <= 200.0 and abs(yError) <= 200.0:
            # 如果可以看到 aruco marker，並且數值沒有爆炸的話，開始調整
            logger.afp_debug("xError: " + str(xError))
            logger.afp_debug("yError: " + str(yError))
            if 0 <= xError <= 20:
                # 當飛機在 Aruco Marker 的右邊
                lrSpeed = 10
            elif -20 <= xError <= 0:
                # 當飛機在 Aruco Marker 的左邊
                lrSpeed = -10
            else:
                lrSpeed = 0

            if 0 <= yError <= 20:
                # 當飛機在 Aruco Marker 下面（銀色夾子在上）
                fbSpeed = -10
            elif -20 <= yError <= 0:
                # 當飛機在 Aruco Marker 上面（銀色夾子在上）
                fbSpeed = 10
            else:
                fbSpeed = 0

            if abs(fbSpeed) > 0 or abs(lrSpeed) > 0:
                # 需要修正，則開始啟動馬達修正
                logger.afp_debug("adjust fb" + str(fbSpeed))
                logger.afp_debug("adjust lr" + str(lrSpeed))
                tello.send_rc_control(lrSpeed, fbSpeed, 0, 0)
            else:
                # 不需要修正，則退出迴圈，回到原本降落程式
                logger.afp_debug("not good2")
                tello.send_rc_control(0, 0, 0, 0)
                break

        else:
            # 沒看到 aruco marker 或數值爆炸，就停止動作
            # TODO: 救回看到 marker 的操控
            logger.afp_debug("not good1")
            tello.send_rc_control(0, 0, 0, 0)


def AutoLandingSecController(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    isTvecExplode = False
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
            if abs(tvec[0][0][0]) <= 2.0 and abs(tvec[0][0][1]) <= 2.0:
                # 檢查 x, y 值有沒有爆掉，沒有才可以使用
                # 取得與 marker 的 x, y 與高的位移量
                xError = int(tvec[0][0][0] * 100)
                yError = int(tvec[0][0][1] * 100)
                hError = int(tvec[0][0][2] * 100)
                isTvecExplode = False
            else:
                isTvecExplode = True

            if not isTvecExplode:
                # 如果 Tvec 沒有炸掉，則可以進入迴圈查看
                if abs(xError) >= 20 and yError >= 20:
                    tello.send_rc_control(0, 0, 0, 0)
                    logger.afp_debug("stop")
                    time.sleep(3)
                    # 如果 xError 與 yError 都大於內建函數最小移動值 20，則可以移動到降落點
                    xError, yError, hError, isSeeMarker = arucoPoseCoordinate(telloFrameBFR, matrix_coefficients,
                                                                              distortion_coefficients, frameSharedVar)
                    logger.afp_debug("xError: " + str(xError))
                    logger.afp_debug("yError: " + str(yError))
                    tello.move_forward(yError)
                    tello.move_right(abs(xError))
                    tello.land()
                    afStateService.end()
                    break
                else:
                    # 如果x或y不到20，則讓他慢慢移動到大於20
                    AdjustDistToTarget(tello, telloFrameBFR, matrix_coefficients,
                                       distortion_coefficients, afStateService, frameSharedVar)
        else:
            logger.afp_debug("not good0")
            tello.send_rc_control(0, 0, 0, 0)


def RvecTest(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar, terminalService):

    while True:

        tello.send_rc_control(0, 0, 0, 0)
        # Update terminal value
        setTerminal(terminalService, tello)
        if terminalService.getForceLanding():
            afStateService.forceLanding()
            tello.land()
            break
        if terminalService.getKeyboardTrigger():
            afStateService.keyboardControl()
            break

        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # Get Post Estimation from Aruco Marker
        centerX, centerY, rvec, tvec, ids = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)
        frameSharedVar.rvec = rvec
        frameSharedVar.tvec = tvec


def TestSpeedFly(tello, telloFrameBFR, matrix_coefficients, distortion_coefficients, afStateService, frameSharedVar):
    tello.send_rc_control(0, -10, 0, 0)
    time.sleep(3)
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(3)
    tello.land()
    afStateService.end()


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
        centerX, centerY, rvec, tvec, ids = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame)

        if rvec is not None and tvec is not None:
            frameSharedVar.rvec = rvec[0][0]
            frameSharedVar.tvec = tvec[0][0]

            # 第一次啟動取 Y 值
            if isFirstTimeGetY:
                # tello.send_rc_control(0, 0, 0, 0)

                centerX, centerY, rvec, tvec, ids = arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients,
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
