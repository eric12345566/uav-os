class CarSocketService(object):

    def __init__(self):
        self.position = ''
        self.isLanding = 'false'

    def setPosition(self, position):
        self.position = position

    def getPosition(self):
        if( 'A0' in self.position):
            return 'A0'
        elif ('A1' in self.position):
            return 'A1'
        elif ('A2' in self.position):
            return 'A2'
        elif ('A3' in self.position):
            return 'A3'
    def getBusState(self):
        if( 'going to' in self.position):
            return 'going to'
        elif( 'arrive' in self.position):
            return 'arrive'
    # status: String
    def setLandingStatus(self, status):
        # print('isLanding: ', status)
        self.isLanding = status

    def getLandingStatus(self):
        return self.isLanding