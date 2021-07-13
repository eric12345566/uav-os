import numpy as np
import cv2 as cv
from module.algo.arucoMarkerDetect import arucoMarkerDetectFrameTest

frame = cv.imread('contours_test.jpg')

frame = arucoMarkerDetectFrameTest(frame)

cv.imshow('test', frame)
cv.waitKey(0)
cv.destroyAllWindows()

