import cv2 as cv


def MarkedFrameProcess(markedFrameService):
    print("MarkedFrameProcess On")
    while not markedFrameService.isMarkedFrameReady():
        pass

    while True:
        markedFrame = markedFrameService.getFrame()
        print("markedFrame: ", markedFrame)
        cv.imshow('markedFrame', markedFrame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cv.destroyAllWindows()
    print("Marked Frame End")