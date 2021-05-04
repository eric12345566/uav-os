import multiprocessing as mp
from multiprocessing.managers import BaseManager
import time
import process.controllerProcess as ctrp
import process.frameProcess as fp


class SimpleClass(object):
    def __init__(self):
        self.frame = []

    def set(self, frame):
        self.frame = frame

    def get(self):
        return self.frame


if __name__ == '__main__':
    # record started time
    startTime = time.time()

    BaseManager.register('SimpleClass', SimpleClass)
    manager = BaseManager()
    manager.start()

    arr1 = manager.SimpleClass()
    # init
    ctrProcess = mp.Process(target=ctrp.controllerProcess, args=('hello controller', arr1,))
    frameProcess = mp.Process(target=fp.frameProcess, args=(arr1,))

    ctrProcess.start()
    frameProcess.start()

    ctrProcess.join()
    frameProcess.join()

    endTime = time.time()

    print("elapsed time: ", endTime - startTime)
