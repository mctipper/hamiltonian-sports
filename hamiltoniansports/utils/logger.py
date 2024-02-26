import logging
from pathlib import Path
from datetime import datetime


class LazyFileHandler(logging.FileHandler):
    """delays the creation of the log file / dir until the log command is received"""

    def _open(self):
        # method overriding, create the dir if not exists
        if not Path(self.baseFilename).parent.is_dir():
            Path(self.baseFilename).parent.mkdir(parents=True, exist_ok=True)
        # running the superclass _open() method creates the logfile
        return super()._open()


class Logger:
    @staticmethod
    def setup(current_datetime: datetime, logname: str = "main"):
        """creates a logger using keyname 'logname'. It is expected that only a single
        logger will be required, however allowing logname to be passed in should
        future requirements warrant it.

        cout / terminal / stream level is INFO
        file level is DEBUG
        """
        # create a generic logger
        logger = logging.getLogger(logname)
        logger.setLevel(logging.DEBUG)

        # create stream/file handlers
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)

        logfilepath = Path(f"./.logs/{current_datetime:%Y%m%d_%H%M}.log")
        if not logfilepath.parent.is_dir():
            logfilepath.parent.mkdir(parents=True, exist_ok=True)

        f_handler = LazyFileHandler(logfilepath)
        f_handler.setLevel(logging.DEBUG)

        # create different formatters and add them to each handler
        c_format = logging.Formatter(
            "%(levelname)-8s - [%(filename)s - %(funcName)s() ] - %(message)s"
        )
        f_format = logging.Formatter(
            "%(asctime)s - %(levelname)-8s - [%(filename)s:%(lineno)s - %(funcName)s() ] --- %(message)s"
        )
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        return logger
