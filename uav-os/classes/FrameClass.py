import multiprocessing as mp

"""
    FrameClass
    共享 Frame 用的類別
"""


class FrameClass(object):
    def __init__(self):
        self.frame = []
        self.address = None
        # self.markedFrame = []
        self.lock = mp.Lock()

        self.__isFrameReady = False
        self.__isMarkedFrameReady = False

    """ Original Frame
    """
    def setFrame(self, frame):
        # self.lock.acquire()
        self.frame = frame
        # self.lock.release()

    def getFrame(self):
        return self.frame

    """ UDP Address
    """
    def setAddress(self, addr):
        self.address = addr

    def getAddress(self):
        return self.address

    """ Is frame ready state 
    """

    def setFrameReady(self):
        self.__isFrameReady = True

    def isFrameReady(self):
        return self.__isFrameReady

    # def afp_frameReady(self):
    #     self.__isMarkedFrameReady = True
    #
    # def isMarkedFrameReady(self):
    #     return self.__isMarkedFrameReady

    # """ Marked frame
    # """
    # def setMarkedFrame(self, markedFrame):
    #     self.lock.acquire()
    #     self.markedFrame = markedFrame
    #     self.lock.release()
    #
    # def getMarkedFrame(self):
    #     return self.markedFrame
