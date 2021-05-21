from djitellopy import Tello
from threading import Thread
import cv2 as cv
from module.BackgroundFrameRead import BackgroundFrameRead


class TelloFrameTest(object):
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()

        self.tello.streamoff()
        self.tello.streamon()

        udpAddr = self.tello.get_udp_video_address()
        self.bfr = BackgroundFrameRead(udpAddr)
        self.bfr.start()
        self.frame = self.bfr.frame
        self.frameWorker = Thread(target=self.showFrameWorker, args=(), daemon=True)

    def showFrame(self):
        while True:
            self.frame = self.bfr.frame
            cv.imshow('frame', self.frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cv.destroyAllWindows()

    def showFrameWorker(self):
        while True:
            print("frame:", self.frame)
            cv.imshow('frame', self.frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cv.destroyAllWindows()

    def run(self):
        self.frameWorker.start()

    def stop(self):
        self.frameWorker.join()


if __name__ == "__main__":
    tft = TelloFrameTest()
    # tft.showFrame()
    tft.run()
    while True:
        pass
    tft.stop()
