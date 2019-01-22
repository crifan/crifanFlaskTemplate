from conf.app import settings
from factory import create_app
from common.FlaskLogSingleton import log
from common.util import getMysqlConnection
from flask import request

################################################################################
# Global Definitions
################################################################################

################################################################################
# Global Variables
################################################################################


################################################################################
# Global Function
################################################################################


################################################################################
# Global Init App
################################################################################

log.info("before create flask app: settings=%s", settings)
app = create_app(settings)
app.app_context().push()
log.info("create flask app complete: app=%s", app)
log.debug("app=%s", app)
log.debug("settings.FLASK_ENV=%s, settings.DEBUG=%s, settings.MONGODB_HOST=%s", settings.FLASK_ENV, settings.DEBUG, settings.MONGODB_HOST)


@app.before_request
def new_mysql_connection():
    mysqlConfigDict = {
        'host': settings.MYSQL_HOST,
        'port': settings.MYSQL_PORT,
        'user': settings.MYSQL_USER,
        'password': settings.MYSQL_PASSWORD,
        'db': settings.MYSQL_DB,
        'charset': settings.MYSQL_CHARSET,
    }
    curReqSqlConn = getMysqlConnection(mysqlConfigDict)
    log.debug("new_mysql_connection: curReqSqlConn=%s", curReqSqlConn)
    request.curReqSqlConn = curReqSqlConn
    log.debug("request.curReqSqlConn=%s", request.curReqSqlConn)

# @app.after_request
# def close_mysql_connection(responseObj):
#     log.debug("close_mysql_connection: responseObj=%s", responseObj)
#     log.debug("request.curReqSqlConn=%s", request.curReqSqlConn)
#     if request.curReqSqlConn:
#         request.curReqSqlConn.close()
#         request.curReqSqlConn = None
#     return responseObj

@app.teardown_request
def close_mysql_connection(curException):
    log.debug("close_mysql_connection: curException=%s", curException)
    log.debug("request.curReqSqlConn=%s", request.curReqSqlConn)
    if request.curReqSqlConn:
        request.curReqSqlConn.close()
        request.curReqSqlConn = None


if __name__ == "__main__":
    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.DEBUG,
        use_reloader=False
    )
