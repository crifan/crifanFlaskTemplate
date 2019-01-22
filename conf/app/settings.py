import os, logging
from os.path import join, dirname
from dotenv import load_dotenv

################################################################################
# Common Settings
################################################################################

DEBUG = False

# makesure even debug, also will execute: app's teardown_request -> to close mysql connection per request
PRESERVE_CONTEXT_ON_EXCEPTION = None

FLASK_PORT = 52100
# FLASK_HOST = "127.0.0.1"
# FLASK_HOST = "localhost"
# Note:
# 1. to allow external access this server
# 2. make sure here gunicorn parameter "bind" is same with here !!!
FLASK_HOST = "0.0.0.0"

# Flask app name
FLASK_APP_NAME = "crifanFlaskTemplate"

# Log File
LOG_LEVEL_FILE = logging.DEBUG
LOG_FORMAT = "[%(asctime)s %(levelname)s %(process)d %(processName)s %(thread)d %(threadName)s %(filename)s:%(lineno)d %(funcName)s] %(message)s"
LOG_FILE_MAX_BYTES = 2 * 1024 * 1024
LOG_FILE_BACKUP_COUNT = 10
# Log Console
LOG_LEVEL_CONSOLE = logging.INFO
LOG_CONSOLE_DATA_FORMAT = '%Y%m%d %I:%M:%S'

# MongoDB
# reuturn file url's host
# FILE_URL_HOST = FLASK_HOST
FILE_URL_HOST = "127.0.0.1"


################################################################################
# Load .env for development/production mode
################################################################################

#FLASK_ENV_DEFAULT = "production"
FLASK_ENV_DEFAULT = "development"
cur_flask_environ = os.getenv("FLASK_ENV")
# print("cur_flask_environ=%s" % cur_flask_environ)
if cur_flask_environ:
    FLASK_ENV = cur_flask_environ
else:
    FLASK_ENV = FLASK_ENV_DEFAULT
print("FLASK_ENV=%s" % FLASK_ENV)
cur_dir = dirname(__file__)
# print("cur_dir=%s" % cur_dir)
env_folder = FLASK_ENV
# print("env_folder=%s" % env_folder)
dotenv_path = os.path.join(cur_dir, env_folder, '.env')
# print("dotenv_path=%s" % dotenv_path)
dotenv_load_ok = load_dotenv(dotenv_path)
# print("dotenv_load_ok=%s" % dotenv_load_ok)

# DEBUG = os.getenv("DEBUG")
# DEBUG = bool(os.getenv("DEBUG"))
debug_str = os.getenv("DEBUG")
if debug_str:
    debug_str_lower = debug_str.lower()
    if (debug_str_lower == "false") or (debug_str_lower == "0"):
        DEBUG = False
    elif (debug_str_lower == "true") or (debug_str_lower == "1"):
        DEBUG = True

MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
if MONGODB_PORT:
    MONGODB_PORT = int(MONGODB_PORT)
MONGODB_ISUSEAUTH = os.getenv("MONGODB_ISUSEAUTH")

if MONGODB_ISUSEAUTH:
    MONGODB_ISUSEAUTH = bool(MONGODB_ISUSEAUTH)
else:
    MONGODB_ISUSEAUTH = False

MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_AUTH_SOURCE = os.getenv("MONGODB_AUTH_SOURCE")
MONGODB_AUTH_MECHANISM = os.getenv("MONGODB_AUTH_MECHANISM")

FILE_URL_HOST = os.getenv("FILE_URL_HOST")

print("After load .env: FLASK_ENV=%s, DEBUG=%s, MONGODB_HOST=%s" % (FLASK_ENV, DEBUG, MONGODB_HOST))


MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PORT = os.getenv("MYSQL_PORT")
if MYSQL_PORT:
    MYSQL_PORT = int(MYSQL_PORT)
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


# Init after FLASK_ENV
LOG_FILE_FILENAME = os.path.join("logs", FLASK_ENV, "%s.log" % FLASK_APP_NAME)

################################################################################
# Flask-Restful
################################################################################

ENDPOINT_USER = "user"

################################################################################
# MongoDB
################################################################################

MONGODB_DB_DB1           = "db1_name"
MONGODB_DB1_COLLECTION_1   = "db1_collection1"

MONGODB_DB_DB2            = "db2_name"
MONGODB_DB2_COLLECTION_1  = "db2_collection1"

# internally compress origin too big (jpg/png/...) image, to speed frontend(miniprogram) load speed
IMAGE_COMPRESS_SIZE = (300, 300)

################################################################################
# Redis
################################################################################

REDIS_URL = "redis://localhost:6379/0"

################################################################################
# SMS Code
################################################################################

SMS_CODE_LENGTH = 6
SMS_CODE_EXPIRE_TIME = 60 * 5 # in seconds
# # for debug
# SMS_CODE_EXPIRE_TIME = 100 # in seconds


################################################################################
# Timezone
################################################################################

TIMEZONE_LOCAL_HOURS = 8 # GMT+8


################################################################################
# Static Files
################################################################################

FILE_PREFIX = "http://%s:%d" % (FILE_URL_HOST, FLASK_PORT)

# FILE_STATIC_URL_PATH = "/ProjectRootPath"
FILE_STATIC_FOLDER = "assets"

FILE_STATIC_IMAGES_PATH = os.path.join(FILE_STATIC_FOLDER, "images")
