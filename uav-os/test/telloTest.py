from enum import Enum
from djitellopy import Tello
import cv2


class FlyState(Enum):
    INIT = 'init'
    READY = 'ready'
    RUN = 'run'
    DONE = 'done'


class FlyCore(object):
    def __init__(self):
        """ Vars for Core
        """
        self.tello = Tello()
        self.frame = None
        self.state = FlyState.INIT

        """ Tello Init
        """
        self.tello.connect()
        # self.tello.set_speed()
        self.tello.streamoff()
        self.tello.streamon()
        self.state = FlyState.READY



    def showFrame(self):
        while True:
            # Get camera frame
            telloFrame = self.tello.get_frame_read()
            self.frame = telloFrame.frame

            cv2.imshow("telloFrame", self.frame)

            # if self.state == FlyState.READY:
            #     self.fly()
            # elif self.state == FlyState.DONE:
            #     print("Fly Done, You Can Exit Now")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        self.tello.streamoff()
        self.tello.end()
        print("Flying Core End")

#     def fly(self):
#         self.state = FlyState.RUN
#         self.tello.takeoff()

#         # tello.move_left(100)
#         self.tello.rotate_counter_clockwise(180)
#         self.tello.move_forward(100)

#         self.tello.land()
#         self.state = FlyState.DONE


if __name__ == "__main__":
    flyCore = FlyCore()
    flyCore.showFrame()