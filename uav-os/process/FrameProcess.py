import cv2 as cv
from State.OSStateEnum import OSState
from service.LoggerService import LoggerService


def FrameProcess(shareFrame, OSStateService):
    logger = LoggerService()
    logger.fp_debug("Start")
    # cap = cv.VideoCapture(0)

    # OSStateService.frameInitReady()
    initCapOneTime = False
    while True:
        # print("ctr: ",OSStateService.getControllerInitState())
        if OSStateService.getControllerInitState():

            if not initCapOneTime:
                address = shareFrame.getAddress()
                cap = cv.VideoCapture(address)
                initCapOneTime = True

            if not cap.isOpened():
                logger.fp_error("VideoCapture not opened")
                exit(-1)

            ret, frame = cap.read()
            frame = cv.flip(frame, 1)
            shareFrame.setFrame(frame)

            if not ret:
                logger.fp_error("frame empty")
                break
            shareFrame.frame_frameReady()

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
            OSStateService.frameInitReady()
    cap.release()
    cv.destroyAllWindows()
    logger.fp_debug("End")


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

            shareFrame.frame_frameReady()
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
