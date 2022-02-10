from djitellopy import Tello
import time

tello = Tello()
tello.connect()
print("battery: ", tello.get_battery())
print("temperature: ", tello.get_temperature())

tello.land()
