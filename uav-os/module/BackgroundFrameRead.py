from threading import Thread
import cv2


class BackgroundFrameRead:
    """
    This class read frames from a VideoCapture in background. Use
    backgroundFrameRead.frame to get the current frame.
    """

    def __init__(self, address):

        self.cap = cv2.VideoCapture(address)

        if not self.cap.isOpened():
            self.cap.open(address)

        self.grabbed, self.frame = self.cap.read()
        if not self.grabbed or self.frame is None:
            raise Exception('Failed to grab first frame from video stream')

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

    def stop(self):
        """Stop the frame update worker
        Internal method, you normally wouldn't call this yourself.
        """
        self.stopped = True
        self.worker.join()