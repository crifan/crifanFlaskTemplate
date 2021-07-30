import os
import logging
from logging.handlers import RotatingFileHandler
from conf.app import settings
from common.ThreadSafeSingleton import ThreadSafeSingleton
# from sys import stdout

def createFolder(folderFullPath):
    """
        create folder, even if already existed
        Note: for Python 3.2+
    """
    os.makedirs(folderFullPath, exist_ok=True)

def init_logger(flask_settings, enableConsole=True):
    print("init_logger")
    flaskAppLogger = logging.getLogger(flask_settings.FLASK_APP_NAME) # <Logger RobotQA (WARNING)>
    print("flaskAppLogger=%s" % flaskAppLogger)
    flaskAppLogger.setLevel(flask_settings.LOG_LEVEL_FILE)

    logFormatter = logging.Formatter(flask_settings.LOG_FORMAT)

    # auto create folder
    logFoder = os.path.dirname(flask_settings.LOG_FILE_FILENAME) # 'logs/development'
    createFolder(logFoder)

    fileHandler = RotatingFileHandler(
        flask_settings.LOG_FILE_FILENAME,
        maxBytes=flask_settings.LOG_FILE_MAX_BYTES,
        backupCount=flask_settings.LOG_FILE_BACKUP_COUNT,
        encoding="UTF-8")
    fileHandler.setLevel(flask_settings.LOG_LEVEL_FILE)
    fileHandler.setFormatter(logFormatter)
    flaskAppLogger.addHandler(fileHandler)

    if enableConsole :
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        # console = logging.StreamHandler(stdout)
        console.setLevel(flask_settings.LOG_LEVEL_CONSOLE)
        # set a format which is simpler for console use
        formatter = logging.Formatter(
            # fmt=logFormatter)
            # fmt=logFormatter,
            fmt=flask_settings.LOG_FORMAT,
            datefmt=flask_settings.LOG_CONSOLE_DATA_FORMAT)
        # tell the handler to use this format
        console.setFormatter(formatter)
        flaskAppLogger.addHandler(console)

    print("init_logger: after init flaskAppLogger%s" % flaskAppLogger)

    return flaskAppLogger

class LoggerSingleton(metaclass=ThreadSafeSingleton):
    curLog = ""

    def __init__(self):
        self.curLog = init_logger(settings)
        # Note: during __init__, AVOID use log, otherwise will deadlock
        # log.info("LoggerSingleton __init__: curLog=%s", self.curLog)
        print("LoggerSingleton __init__: curLog=%s" % self.curLog)

logSingleton = LoggerSingleton()
log = logSingleton.curLog
log.info("LoggerSingleton inited, logSingleton=%s", logSingleton) # <factory.LoggerSingleton object at 0x10cbcafd0>
log.info("log=%s", log) # <Logger RobotQA (DEBUG)>

# # debug for singleton log
# log2 = LoggerSingleton()
# print("log2=%s" % log2)
