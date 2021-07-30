import numpy as np
import cv2 as cv

from module.indoorLocationAlgo.QrcodePositionAlgo import streamDecode


# Transfer location ID to (x, y) value
def transferLocationID(x):
    return {
        '-1': (-1, -1),
        '2': (10, 10),
        '3': (30, 30),
        '7': (70, 70),
        '9': (90, 90)
    }[x]



def indoorLocationWorker(telloFrameBFR, indoorLocationShared):
    count = 1
    while True:
        frame = telloFrameBFR.frame
        count += 1
        # _, frame = cap.read()
        if count % 1 == 0:
            rotateAngle, qrPosition, _ = streamDecode(frame)
            # print('---------------Estimate Analytics----------------')
            # print('Rotate Angle: ' + str(rotateAngle))
            # print('Qrcode Position: ' + str(qrPosition))
            # print('-------------------------------------------------')
            indoorLocationShared.x_location, indoorLocationShared.y_location = transferLocationID(str(qrPosition))
            indoorLocationShared.direction = rotateAngle
        print('hahaha')
        print(indoorLocationShared.direction)

    # x, y, dirt = indoorLocationAlgo(frame)

    # indoorLocationShared.x_location = x
    # indoorLocationShared.y_location = x
