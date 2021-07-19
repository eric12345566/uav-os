import numpy as np
import cv2 as cv


def indoorLocationWorker(telloFrameBFR, indoorLocationShared):
    frame = telloFrameBFR.frame

    # x, y, dirt = indoorLocationAlgo(frame)

    # indoorLocationShared.x_location = x
    # indoorLocationShared.y_location = x
