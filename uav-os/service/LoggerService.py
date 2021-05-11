import sys
import logging

class _AnsiColorizer(object):
    """
    A colorizer is an object that loosely wraps around a stream, allowing
    callers to write text to the stream in a particular color.

    Colorizer classes must implement C{supported()} and C{write(text, color)}.
    """
    _colors = dict(black=30, red=31, green=32, yellow=33,
                   blue=34, magenta=35, cyan=36, white=37)

    def __init__(self, stream):
        self.stream = stream

    @classmethod
    def supported(cls, stream=sys.stdout):
        """
        A class method that returns True if the current platform supports
        coloring terminal output using this method. Returns False otherwise.
        """
        if not stream.isatty():
            return False  # auto color only on TTYs
        try:
            import curses
        except ImportError:
            return False
        else:
            try:
                try:
                    return curses.tigetnum("colors") > 2
                except curses.error:
                    curses.setupterm()
                    return curses.tigetnum("colors") > 2
            except:
                raise
                # guess false in case of error
                return False

    def write(self, text, color):
        """
        Write the given text to the stream in the given color.

        @param text: Text to be written to the stream.

        @param color: A string label for a color. e.g. 'red', 'white'.
        """
        color = self._colors[color]
        self.stream.write('\x1b[%s;1m%s\x1b[0m' % (color, text))


class ColorHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stderr):
        super(ColorHandler, self).__init__(_AnsiColorizer(stream))

    def emit(self, record):
        msg_colors = {
            logging.DEBUG: "green",
            logging.INFO: "blue",
            logging.WARNING: "yellow",
            logging.ERROR: "red"
        }

        color = msg_colors.get(record.levelno, "blue")
        self.stream.write(record.msg + "\n", color)


class LoggerService(object):
    def __init__(self):
        # LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
        LOGGING_FORMAT = ''
        DATE_FORMAT = '%Y%m%d %H:%M:%S'
        logging.getLogger().setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT, datefmt=DATE_FORMAT)
        # logging.getLogger().addHandler(ColorHandler())

        # TODO: Mode for log bound
        self.Mode = "dev"
        self.controllerProcessName = "CTRP"
        self.autoFlightProcessName = "AFP"
        self.frameProcessName = "FP"

    """ Normal Debug
    """
    def ctrp_debug(self, logString):
        logging.debug("[" + self.controllerProcessName + "] <DEBUG>: " + logString)

    def afp_debug(self, logString):
        logging.debug("[" + self.autoFlightProcessName + "] <DEBUG>: " + logString)

    def fp_debug(self, logString):
        logging.debug("[" + self.frameProcessName + "] <DEBUG>: " + logString)

    """ Info
    """

    def ctrp_info(self, logString):
        logging.info("[" + self.controllerProcessName + "] <INFO>: " + logString)

    def afp_info(self, logString):
        logging.info("[" + self.autoFlightProcessName + "] <INFO>: " + logString)

    def fp_info(self, logString):
        logging.info("[" + self.frameProcessName + "] <INFO>:" + logString)

    """ Error Log
    """
    def ctrp_error(self, logString):
        logging.error("[" + self.controllerProcessName + "] <ERROR>: " + logString)

    def afp_error(self, logString):
        logging.error("[" + self.autoFlightProcessName + "] <ERROR>: " + logString)

    def fp_error(self, logString):
        logging.error("[" + self.frameProcessName + "] <ERROR>: " + logString)

    """ Warning Log
    """
    def ctrp_warning(self, logString):
        logging.error("[" + self.controllerProcessName + "] <WARNING>: " + logString)

    def afp_warning(self, logString):
        logging.error("[" + self.autoFlightProcessName + "] <WARNING>: " + logString)

    def fp_warning(self, logString):
        logging.error("[" + self.frameProcessName + "] <WARNING>: " + logString)
