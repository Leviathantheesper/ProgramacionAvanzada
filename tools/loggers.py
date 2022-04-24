
"""
Minimal functions to use loggers in a program

F. Sagols
March 22nd 2022
CDMX
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from os import path
import os


def ensure_path_existence(test_path):
    """
    Given a valid file system path this method verifies its existence.
    Otherwise, it creates the path. If we want to prove the existence of a
    directory we should append a '/' at the end of test_path.

    PARAMETERS
    ----------
    test_path : str
        The path referred above.

    Examples
    --------
    >>> ensure_path_existence(
    ... "./ib_activity_reports/DU2876788/DU2876788_20210215_20210219.csv")
    True
    >>> ensure_path_existence(
    ... "./logs/")
    True
    """
    elements = test_path.split("/")
    if not elements:
        raise ValueError("Empty path detected")

    sub_path = ''
    for index, element in enumerate(elements):
        sub_path = sub_path + element + '/'
        if index == len(elements) - 1:
            sub_path = sub_path[0:-1]
            if element == '':
                return True
            else:
                return os.path.isfile(sub_path)
        else:
            if sub_path != '' and not path.exists(sub_path):
                # print("%s does not exist. Creating it." % sub_path)
                os.mkdir(sub_path)


def define_logger(logger_file):
    """
    Returns a logger. See module logging.
    The path '.logs' must exit. Otherwise, it is created.
    This method differs from ib_logs.get_logger. That is used with the database
    to create the logger in logging.conf. In this version only a 'static' logger
    is defined.

    Parameters
    ----------
    logger_file : str
        File name of the logger
    Returns
    -------
        logger
    """
    ensure_path_existence('./logs/')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_handler = TimedRotatingFileHandler('./logs/' + logger_file,
                                           when="midnight")
    log_formatter = logging.Formatter(
        '%(asctime)s-%(name)s-%(levelname)s-%(pathname)s-%(lineno)s-  '
        '%(message)s')
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger(logger_file)
    logger.addHandler(log_handler)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
    return logger


a = 5
b = 10
c = 20
