import time
import cv2 as cv
from State.OSStateEnum import OSState


def AutoFlightProcess(uavFrame, OSStateService, FlightCmdService):
    print("Auto")