class CarSocketService(object):

    def __init__(self):
        self.position = 'A0'
        self.isLanding = 'false'

    def setPosition(self, position):
        self.position = position

    def getPosition(self):
        if( 'A1' in self.position):
            return 'A1'
        elif ('A2' in self.position):
            return 'A2'
        elif ('A3' in self.position):
            return 'A3'
        elif ('A4' in self.position):
            return 'A4'

    # status: String
    def setLandingStatus(self, status):
        self.isLanding = status

    def getLandingStatus(self):
        return self.isLanding