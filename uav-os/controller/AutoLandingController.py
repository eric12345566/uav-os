from simple_pid import PID
import numpy as np
import cv2 as cv

# Algo
from module.algo.arucoMarkerDetect import arucoMarkerDetect, arucoMarkerDetectFrame


def autoLandingController(tello, telloFrameBFR, afStateService, frameSharedVar, logger):
    lrPID = PID(0.35, 0.0001, 0.1)
    lrPID.output_limits = (-100, 100)
    fbPID = PID(0.35, 0.0001, 0.1)
    fbPID.output_limits = (-100, 100)
    for_back_velocity = 0
    left_right_velocity = 0
    up_down_velocity = 0
    yaw_velocity = 0
    canLanding = False

    # Landing procedure
    while True:
        # Process frame
        frame = telloFrameBFR.frame
        frame = cv.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape

        # ArUco Marker Detect
        corners, ids, rejectedImgPoints = arucoMarkerDetect(frame)

        if np.all(ids is not None):
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

            frameSharedVar.setLrError(lrError)
            frameSharedVar.setLrPID(left_right_velocity)

            # front-back
            fbError = y_centerPixel - frameHeight // 2
            for_back_velocity = fbPID(fbError)
            for_back_velocity = -int(for_back_velocity) // 3

            frameSharedVar.setFbError(fbError)
            frameSharedVar.setFbPID(for_back_velocity)

            # 偵測是否可以下降
            if abs(fbError) < 20 and abs(lrError) < 20:
                canLanding = True
                for_back_velocity = 0
                left_right_velocity = 0
        else:
            left_right_velocity = 0
            for_back_velocity = 0

        if not canLanding:
            # cmdUavRunOnce(FlightCmdService, CmdEnum.send_rc_control, [left_right_velocity, for_back_velocity,
            #                                                           up_down_velocity, yaw_velocity])
            tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
        else:
            # cmdUavRunOnce(FlightCmdService, CmdEnum.send_rc_control, [left_right_velocity, for_back_velocity,
            #                                                           up_down_velocity, yaw_velocity])
            tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            # 已經對準到可以下降的狀況，進行下降
            # now_height = uavGetInfo(CmdEnum.get_distance_tof, FlightCmdService)
            now_height = tello.get_distance_tof()
            logger.afp_debug("now_height: " + str(now_height))
            frameSharedVar.landHeight = now_height
            move_down_cm = 0

            # 檢查高度來決定下降方式
            if 20 <= now_height <= 30:
                # 如果高度已經在 20 ~ 30 cm 之間，直接下降
                # cmdUavRunOnce(FlightCmdService, CmdEnum.land, 0)
                tello.land()
                afStateService.landed()
                break
            else:
                # 否則，先降低一點高度
                if now_height // 2 > 30:
                    move_down_cm = int(now_height - now_height // 2)
                    logger.afp_debug("move_down_cm: " + str(move_down_cm))
                    # cmdUavRunOnce(FlightCmdService, CmdEnum.move_down, move_down_cm)
                    tello.move_down(move_down_cm)
                else:
                    move_down_cm = int(now_height - 30)
                    if move_down_cm < 20:
                        # cmdUavRunOnce(FlightCmdService, CmdEnum.land, 0)
                        tello.land()
                        afStateService.landed()
                        break
                    else:
                        logger.afp_debug("move_down_cm: " + str(move_down_cm))
                        # cmdUavRunOnce(FlightCmdService, CmdEnum.move_down, move_down_cm)
                        tello.move_down(move_down_cm)

            canLanding = False