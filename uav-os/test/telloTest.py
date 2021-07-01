from djitellopy import Tello
import time

tello = Tello()
tello.connect()
print("battery: ", tello.get_battery())
print("temperature: ", tello.get_temperature())
# tello.takeoff()
# time.sleep(10)
# tello.land()
