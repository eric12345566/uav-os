"""
    FrameClass
    共享 Frame 用的類別
"""


class FrameClass(object):
    def __init__(self):
        self.frame = []

    def set(self, frame):
        self.frame = frame

    def get(self):
        return self.frame
