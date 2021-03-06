from threading import Thread
import cv2


class BackgroundFrameRead:
    """
    This class read frames from a VideoCapture in background. Use
    backgroundFrameRead.frame to get the current frame.
    """

    def __init__(self, address):

        self.cap = cv2.VideoCapture(address)
        # self.frameService = frameService

        if not self.cap.isOpened():
            self.cap.open(address)

        self.grabbed, self.frame = self.cap.read()
        while not self.grabbed or self.frame is None:
            self.grabbed, self.frame = self.cap.read()

        self.stopped = False
        self.worker = Thread(target=self.update_frame, args=(), daemon=True)

    def start(self):
        """Start the frame update worker
        Internal method, you normally wouldn't call this yourself.
        """
        self.worker.start()

    def update_frame(self):
        """Thread worker function to retrieve frames from a VideoCapture
        Internal method, you normally wouldn't call this yourself.
        """
        while not self.stopped:
            if not self.grabbed or not self.cap.isOpened():
                self.stop()
            else:
                self.grabbed, self.frame = self.cap.read()
                # self.frameService.setFrame(self.frame)
                # self.frameService.setFrame(self.frame)

    def stop(self):
        """Stop the frame update worker
        Internal method, you normally wouldn't call this yourself.
        """
        self.stopped = True
        self.worker.join()