from threading import Thread
import cv2 as cv


def frameWorker():
    cap = cv.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv.imshow('frame', frame)
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    worker = Thread(target=frameWorker, args=(), daemon=True)
    worker.start()
    worker.join()

    # frameWorker()