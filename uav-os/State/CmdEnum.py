from enum import Enum


class CmdEnum(Enum):
    move_forward = 'move_forward'
    move_back = 'move_back'
    move_left = 'move_left'
    move_right = 'move_right'
    move_down = 'move_down'
    move_up = 'move_up'
    land = 'land'
    takeoff = 'takeoff'
    emergency = 'emergency'
    rotate_clockwise = 'rotate_clockwise'
    send_rc_control = 'send_rc_control'

    """ Info
    """
    get_battery = 'get_battery'
    get_height = 'get_height'
    get_distance_tof = 'get_distance_tof'
