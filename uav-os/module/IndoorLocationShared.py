class IndoorLocationShared:
    def __init__(self):
        self.x_location = 0
        self.y_location = 0
        self.direction = 0

    def getLocation(self):
        return self.x_location, self.y_location, self.direction
