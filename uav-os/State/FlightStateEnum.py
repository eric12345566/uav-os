from enum import Enum


class FlightState(Enum):
    INIT_SYSTEM = 'init_system'
    READY = 'ready'
    RUNNING = 'running'
