class CarSocketService(object):

    def __init__(self):
        self.position = 0

    def setPosition(self, position):
        self.position = position

    def getPosition(self):
        return int(self.position)