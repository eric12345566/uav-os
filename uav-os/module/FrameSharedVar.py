
class FrameSharedVar:
    def __init__(self):
        self.lrError = 0
        self.lrPID = 0
        self.fbError = 0
        self.fbPID = 0
        self.landHeight = 0

    """ LrError & LrPID
    """
    def setLrError(self, lrError):
        self.lrError = lrError

    def getLrError(self):
        return self.lrError

    def setLrPID(self, lrPID):
        self.lrPID = lrPID

    def getLrPID(self):
        return self.lrPID

    """ FbError & FbPID
    """
    def setFbError(self, fbError):
        self.fbError = fbError

    def getFbError(self):
        return self.fbError

    def setFbPID(self, fbPID):
        self.fbPID = fbPID

    def getFbPID(self):
        return self.fbPID
