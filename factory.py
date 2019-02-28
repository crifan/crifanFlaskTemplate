import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_redis import FlaskRedis
from flask import g
from pymongo import MongoClient
from gridfs import GridFS
from conf.app import settings
from common.FlaskLogSingleton import log
from common.util import generateMongoUri, getMysqlConnection

################################################################################
# Global Variables
################################################################################


################################################################################
# Global Function
################################################################################

def create_app(config_object, init_extensions=True):
    # global log
    log.debug("Flask create_app: config_object=%s, init_extensions=%s", config_object, init_extensions)

    app = Flask(config_object.FLASK_APP_NAME, static_folder=settings.FILE_STATIC_FOLDER)
    log.info("flask app init complete: app=%s", app)
    CORS(app)
    log.debug("flask CORS app init complete")

    log.debug("before init log: app.logger=%s", app.logger) # <Logger flask.app (DEBUG)>
    app.logger = log
    log.debug("after  init log: app.logger=%s", app.logger) # <Logger RobotQA (DEBUG)>

    app.config.from_object(config_object)
    log.info("flask app config from_object complete")
    with app.app_context():
        g.app = app

        log.debug("after load from object: app.config=%s", app.config)
        log.debug('app.config["DEBUG"]=%s, app.config["MONGODB_HOST"]=%s', app.config["DEBUG"], app.config["MONGODB_HOST"])

        if init_extensions:
            register_extensions(app)
            log.info("flask app extensions init completed")

    return app


def register_extensions(app):
    mongo = create_mongo(app)
    g.mongo = mongo
    log.info("mongo=%s", mongo)
    mongoServerInfo = mongo.server_info()
    # log.debug("mongoServerInfo=%s", mongoServerInfo)

    db_flask_template, collection_car, gridfs_files = create_mongo_collection(mongo)
    g.mongoDbFlaskTemplate = db_flask_template
    g.mongoDbFlaskTemplateCollectionCar = collection_car
    g.mongoDbFlaskTemplateGridfsFiles = gridfs_files

    mysql_connection = create_mysql_connection(app)
    g.sqlConn = mysql_connection
    g.sqlConn.isUseLog = False

    # redis_store = FlaskRedis(app)
    # Note: support later get out value is str, not bytes
    redis_store = FlaskRedis(app, charset="utf-8", decode_responses=True)
    g.redisStore = redis_store

    api = create_rest_api(app)
    log.debug("api=%s", api)
    g.api = api

    return app


def create_rest_api(app):
    from modules.user import UserAPI
    from modules.car import CarAPI
    from modules.files import FileFlaskTemplateFilesAPI

    rest_api = Api()

    rest_api.add_resource(UserAPI, '/user', endpoint=settings.ENDPOINT_USER)
    rest_api.add_resource(CarAPI, '/car', endpoint=settings.ENDPOINT_CAR)
    rest_api.add_resource(FileFlaskTemplateFilesAPI,
                          settings.FILE_PREFIX_ENDPOINT_FLASK_TEMPLATE_FILES,
                          settings.FILE_PREFIX_ENDPOINT_FLASK_TEMPLATE_FILES + '/<fileId>',
                          settings.FILE_PREFIX_ENDPOINT_FLASK_TEMPLATE_FILES + '/<fileId>/<fileName>',
                          endpoint=settings.ENDPOINT_FILE_FLASK_TEMPLATE_FILES)

    rest_api.init_app(app)
    return rest_api

def create_mysql_connection(app):
    mysqlConfigDict = {
        'host': settings.MYSQL_HOST,
        'port': settings.MYSQL_PORT,
        'user': settings.MYSQL_USER,
        'password': settings.MYSQL_PASSWORD,
        'db': settings.MYSQL_DB,
        'charset': settings.MYSQL_CHARSET,
    }
    return getMysqlConnection(mysqlConfigDict)

def create_mongo(app):
    mongo_uri = generateMongoUri(
        host=settings.MONGODB_HOST,
        port=int(settings.MONGODB_PORT),
        isUseAuth= settings.MONGODB_ISUSEAUTH,
        username=settings.MONGODB_USERNAME,
        password=settings.MONGODB_PASSWORD,
        authSource=settings.MONGODB_AUTH_SOURCE,
        authMechanism=settings.MONGODB_AUTH_MECHANISM,
    )
    mongo_client = MongoClient(mongo_uri)

    return mongo_client


def create_mongo_collection(mongo_client):
    # Pure PyMongo
    db_flask_template = mongo_client[settings.MONGODB_DB_FLASK_TEMPLATE]
    collection_car = db_flask_template[settings.MONGODB_FLASK_TEMPLATE_COLLECTION_CAR]

    gridfs_files = GridFS(db_flask_template, settings.MONGODB_FLASK_TEMPLATE_GRIDFS_FILES)

    return (db_flask_template, collection_car, gridfs_files)
