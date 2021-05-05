"""
    FrameClass
    共享 Frame 用的類別
"""


class FrameClass(object):
    def __init__(self):
        self.frame = []
        self.address = None

    def setFrame(self, frame):
        self.frame = frame

    def get(self):
        return self.frame

    def setAddress(self, addr):
        self.address = addr

    def getAddress(self):
        return self.address