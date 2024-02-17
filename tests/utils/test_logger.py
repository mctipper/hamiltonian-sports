import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

from datetime import datetime
import logging

from hamiltoniansports.utils.logger import Logger


def test_logger():
    """testing that expected logging setup is present. If future logging requirements change, this will
    obviously need to altered.
    """

    logger = Logger.setup(datetime.now(), "test")

    # ensure two loggers
    assert len(logger.handlers) == 2, "Logger requires two handlers"

    # ensure different types
    assert type(logger.handlers[0]) is not type(
        logger.handlers[1]
    ), "Handlers should be of different types"

    # ensure only correct handler types and logging levels
    for handler in logger.handlers:
        assert isinstance(
            handler, (logging.StreamHandler, logging.FileHandler)
        ), "Wrong handler type"
        if isinstance(handler, logging.FileHandler):
            # note- FileHandler must be checked first since FileHandler inherits from StreamHandler
            assert handler.level == logging.DEBUG, "File handler must be set to DEBUG"
        elif isinstance(handler, logging.StreamHandler):
            assert handler.level == logging.INFO, "Stream handler must be set to INFO"
