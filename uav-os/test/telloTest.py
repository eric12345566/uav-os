from djitellopy import Tello
import time


tello = Tello()


# tello.send_rc_control(0, 30, 0, 0)
# time.sleep(5)
# tello.send_rc_control(0, 0, 0, 0)
# time.sleep(5)
# tello.land()


def flyForwardCm():
    tello.send_rc_control(0, 20, 0, 0)
    time.sleep(1)
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(3)


if __name__ == "__main__":
    tello.connect()
    print("battery: ", tello.get_battery())
    print("temperature: ", tello.get_temperature())
    tello.takeoff()

    flyForwardCm(10)
    tello.land()
