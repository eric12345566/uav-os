from enum import Enum


class FlightState(Enum):
    INIT_SYSTEM = 'init_system'
    READY_FOR_CMD = 'ready_for_cmd'
    INPUT_CMD = 'input_cmd'
    RUNNING_CMD = 'running_cmd'
    DONE = 'done'
    GET_INFO = 'get_info'
    FORCE_LAND = 'force_land'
    ERROR = 'error'
