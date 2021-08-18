""" Set terminal value
"""
def setTerminal(terminalService, tello):
    terminal_class = ['pitch', 'roll', 'yaw', 'battery', 'low_temperature', 'high_temperature', 'temperature', 'barometer', 'high']
    terminal_value_class = []
    terminal_value_class.append(tello.get_pitch())
    terminal_value_class.append(tello.get_roll())
    terminal_value_class.append(tello.get_yaw())
    terminal_value_class.append(tello.get_battery())
    terminal_value_class.append(tello.get_lowest_temperature())
    terminal_value_class.append(tello.get_highest_temperature())
    terminal_value_class.append(tello.get_temperature())
    terminal_value_class.append(tello.get_barometer())
    terminal_value_class.append(tello.get_distance_tof())

    for key in terminal_class:
        index = terminal_class.index(key)
        terminalService.setInfo(key, terminal_value_class[index])
