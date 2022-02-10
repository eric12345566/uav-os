class ArucoMarkerShared:
    def __init__(self):
        self.nowPoint = None
        self.lastPoint = None
        self.markerID = None

    def updatePoint(self, point, markerID):
        self.lastPoint = self.nowPoint
        self.nowPoint = point

        if self.markerID != markerID:
            print(f"ArucoMarkerShared: last id: {self.markerID}, switch to {markerID}")
            self.markerID = markerID

    def getNowPoint(self):
        return self.nowPoint

    def getLastPoint(self):
        return self.lastPoint
