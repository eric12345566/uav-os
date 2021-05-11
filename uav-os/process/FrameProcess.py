import cv2 as cv
from State.OSStateEnum import OSState
from service.LoggerService import LoggerService


def FrameProcess(shareFrame, OSStateService):
    logger = LoggerService()
    logger.fp_debug("Start")
    # cap = cv.VideoCapture(0)

    # OSStateService.frameInitReady()
    if OSStateService.getMode() != 'test':
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
                shareFrame.setFrame(frame)

                if not ret:
                    logger.fp_error("frame empty")
                    break

                cv.imshow('frame', frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
                OSStateService.frameInitReady()
        cap.release()
        cv.destroyAllWindows()
        logger.fp_debug("End")
    else:
        logger.fp_debug("In Testing mode, Not open Frame")
        OSStateService.frameInitReady()

