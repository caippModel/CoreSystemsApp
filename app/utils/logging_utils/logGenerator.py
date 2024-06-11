import logging
from app.utils.logging_utils.colorFormat import ColoredFormatter

class Logger():
    logFormat: str
    logFile: str = 'application.log'

    def __init__(self, logFormat: str, logFile: str) -> None:
        self.logFormat = logFormat
        self.logFile = logFile

    def generateLogger(self) -> logging.Logger:
        """Creates logger

        :return: logger instance
        :rtype: logging.Logger
        """        
        logger = logging.getLogger("logger")
        logLevel = logging.DEBUG
        logger.setLevel(logLevel)

        # Check if the logger already has handlers
        if not logger.handlers:
            # Creates console handler and set level
            ch = logging.StreamHandler()
            ch.setLevel(logLevel)

            # Creates file handler and set level
            fh = logging.FileHandler(self.logFile)
            fh.setLevel(logLevel)

            # Creates formatter
            formatter = ColoredFormatter(self.logFormat, datefmt='%m/%d/%Y, %I:%M:%S %p')

            # Add formatter
            ch.setFormatter(formatter)
            fh.setFormatter(formatter)

            # Add handlers to logger
            logger.addHandler(ch)
            logger.addHandler(fh)

        return logger