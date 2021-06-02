import cv2 as cv
import time
from State.OSStateEnum import OSState
from State.FlightStateEnum import FlightState
from service.LoggerService import LoggerService
from State.CmdEnum import CmdEnum
from module.BackgroundFrameRead import BackgroundFrameRead


def FrameProcess(FrameService, OSStateService, FlightCmdService):
    """ 顯示Frame用，主要使用 cv.imshow() 顯示 frame
    """
    logger = LoggerService()
    logger.fp_debug("Start")

    # Frame Init OK
    OSStateService.frameInitReady()

    # Wait For Controller Ready
    while not FrameService.isFrameReady():
        pass

    # Show frame
    while True:
        frame = FrameService.getFrame()

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            FlightCmdService.forceLand()
            break
    cv.destroyAllWindows()
    logger.fp_debug("End")


# 拋棄，目前所有測試請使用Tello來進行
def FrameProcessTest(shareFrame, OSStateService):
    logger = LoggerService()
    logger.fp_debug("Start")
    """ 用本機電腦當測試
           """
    logger.fp_debug("In Testing mode, Not open Frame")
    cap = cv.VideoCapture(0)
    OSStateService.frameInitReady()
    while True:
        # print("ctr: ",OSStateService.getControllerInitState())
        if OSStateService.getControllerInitState():

            if not cap.isOpened():
                logger.fp_error("VideoCapture not opened")
                exit(-1)

            ret, frame = cap.read()
            shareFrame.setFrame(frame)

            if not ret:
                logger.fp_error("frame empty")
                break

            shareFrame.setFrameReady()
            # while not markedFrameService.isMarkedFrameReady():
            #     pass
            #
            # markedFrame = markedFrameService.getFrame()

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
            OSStateService.frameInitReady()
    cap.release()
    cv.destroyAllWindows()
    logger.fp_debug("End")
