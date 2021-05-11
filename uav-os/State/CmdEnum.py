from enum import Enum


class CmdEnum(Enum):
    move_forward = 'move_forward'
    move_left = 'move_left'
    move_right = 'move_right'
    move_up = 'move_up'
    land = 'land'
    takeoff = 'takeoff'
    emergency = 'emergency'
    rotate_clockwise = 'rotate_clockwise'
    """ Info
    """
    get_battery = 'get_battery'
    get_height = 'get_height'
