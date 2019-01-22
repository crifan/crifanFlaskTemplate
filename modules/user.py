from werkzeug.exceptions import *
from flask import jsonify
from flask import request
from flask import g
from flask_restful import Resource
from flask_restful import reqparse
from common.FlaskLogSingleton import log
# from conf.app import settings
from common.util import getCurUtcTime, getCurLocalTime, genRespFailDict

mongoDb1 = g.mongoDb1
mongoDb1Collection1 = g.mongoDb1Collection1
mongoDb2 = g.mongoDb2
mongoDb2Collection1 = g.mongoDb2Collection1
sqlConn = g.sqlConn
redisStore = g.redisStore

#----------------------------------------
# Util Functions
#----------------------------------------

def mysqlGetLastInsertId(sqlConn):
    lastInsertId = None
    lastInsertIdSql = "SELECT LAST_INSERT_ID()"
    # log.debug("lastInsertIdSql=%s", lastInsertIdSql)
    getLastInsertIdOk, resultDict = sqlConn.executeSql(lastInsertIdSql)
    # log.debug("%s -> %s, %s", lastInsertIdSql, getLastInsertIdOk, resultDict)

    if getLastInsertIdOk:
        # {'code': 0, 'message': 'OK', 'data': [{'LAST_INSERT_ID()': 17}]}
        lastInsertId = resultDict["data"][0]["LAST_INSERT_ID()"]

    # log.debug("lastInsertId=%s", lastInsertId)
    return lastInsertId


#----------------------------------------
# Flask API Functions
#----------------------------------------

class UserAPI(Resource):

    # def get(self):
    #     log.info("UserAPI GET")
    #
    #     # curReqSqlConn = request.curReqSqlConn
    #     # log.debug("curReqSqlConn=%s", curReqSqlConn)
    #
    #     respDict = {
    #         "code": 200,
    #         "message": "get user info ok",
    #         "data": {}
    #     }
    #
    #     parser = reqparse.RequestParser()
    #     parser.add_argument('key1Str', type=str, help="query string parameter 1")
    #     parser.add_argument('key2Int', type=int, help="query string parameter 2")
    #
    #     parsedArgs = parser.parse_args()
    #     log.debug("parsedArgs=%s", parsedArgs)
    #
    #     if not parsedArgs:
    #         return genRespFailDict(BadRequest.code, "Fail to parse input parameters")
    #
    #     key1StrValue = parsedArgs["key1Str"]
    #     key2IntValue = parsedArgs["key2Int"]
    #     log.debug("key1StrValue=%s, key2IntValue=%s", key1StrValue, key2IntValue)
    #
    #     if not key1StrValue:
    #         return genRespFailDict(BadRequest.code, "Empty parameter key1StrValue")
    #
    #     respCurUtcTime = getCurUtcTime()
    #     respCurLocalTime = getCurLocalTime()
    #     respData = {
    #         "key1Str": key1StrValue,
    #         "key2Int": key2IntValue,
    #         "curUtcTime": respCurUtcTime,
    #         "curLocalTime": respCurLocalTime
    #     }
    #
    #     respDict["data"] = respData
    #     return jsonify(respDict)


    def post(self):
        log.info("UserAPI POST")

        respDict = {
            "code": 200,
            "message": "Create user ok",
            "data": {}
        }

        # respUserDict = {
        #     "id": "",
        #
        #     "createTime": "",
        #     "updatedTime": "",
        #     "lastActiveTime": "",
        #
        #     "phone": "",
        #     "name": "",
        # }

        reqParaJson = request.get_json()
        log.debug("reqParaJson=%s", reqParaJson)

        if not reqParaJson:
            return genRespFailDict(BadRequest.code, "Invalid input parameters")

        keyList = []
        valueList = []

        if "phone" in reqParaJson:
            phone = reqParaJson["phone"]

            if phone:
                # check existed or not
                foundByPhoneSql = "SELECT * FROM `user` WHERE phone = '%s'" % phone
                existedUserOk, resultDict = sqlConn.executeSql(foundByPhoneSql)
                log.debug("%s -> %s, %s", foundByPhoneSql, existedUserOk, resultDict)
                if existedUserOk and resultDict["data"]:
                    # found existed user
                    return genRespFailDict(BadRequest.code, "Fail to create user for duplicated phone %s" % phone)

            keyList.append("`phone`")
            valueList.append("'%s'" % phone)

        if "name" in reqParaJson:
            name = reqParaJson["name"]

            keyList.append("`name`")
            valueList.append("'%s'" % name)

        curTime = getCurUtcTime()
        log.debug("curTime=%s", curTime)

        keyList.append("`createdTime`")
        valueList.append("'%s'" % curTime)
        keyList.append("`updatedTime`")
        valueList.append("'%s'" % curTime)
        keyList.append("`lastActiveTime`")
        valueList.append("'%s'" % curTime)

        keyListStr = ",".join(keyList) # '`phone`,`name`,`createdTime`,`updatedTime`,`lastActiveTime`'
        valueListStr = ",".join(valueList) # '\\'13800001111\\',\\'crifan\\',\\'2019-01-22 11:14:29.246945\\',\\'2019-01-22 11:14:29.246945\\',\\'2019-01-22 11:14:29.246945\\''

        # create user
        createUserSql = "INSERT INTO `user` (%s) VALUES(%s)" % (keyListStr, valueListStr)
        createUserOk, resultDict = sqlConn.executeSql(createUserSql)
        log.debug("%s -> %s, %s", createUserSql, createUserOk, resultDict)

        if createUserOk:
            newUserId = mysqlGetLastInsertId(sqlConn)

            return self.respFullUserInfo(respDict, newUserId)
        else:
            return genRespFailDict(InternalServerError.code, "Fail to create new user")


    def get(self):
        log.info("UserAPI GET")

        # curReqSqlConn = getMysqlConnection()
        curReqSqlConn = request.curReqSqlConn
        # log.debug("curReqSqlConn=%s", curReqSqlConn)

        respDict = {
            "code": 200,
            "message": "Get user ok",
            "data": {}
        }

        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, help="user id")

        parsedArgs = parser.parse_args()
        log.debug("parsedArgs=%s", parsedArgs)

        if not parsedArgs:
            return genRespFailDict(BadRequest.code, "Fail to parse input parameters")

        userIdStr = parsedArgs["id"]
        if not userIdStr:
            return genRespFailDict(BadRequest.code, "Fail to get user for empty user id")

        userId = int(userIdStr)

        existedUserSql = "SELECT * FROM `user` WHERE id = %d" % userId
        log.debug("existedUserSql=%s", existedUserSql)
        existedUserOk, resultDict = sqlConn.executeSql(existedUserSql)
        log.debug("%s -> %s, %s", existedUserSql, existedUserOk, resultDict)
        if (not existedUserOk) or (not resultDict["data"]):
            return genRespFailDict(NotFound.code, "Can not found user from id %s" % userId)

        existedUser = resultDict["data"][0]
        log.debug("existedUser=%s", existedUser)

        # update lastActiveTime
        lastActiveTime = getCurUtcTime()
        self.updateUserTime(curSqlConn=curReqSqlConn, userId=userId, lastActiveTime=lastActiveTime)

        respDict["data"] = existedUser
        return jsonify(respDict)


    def put(self):
        log.info("UserAPI PUT")

        respDict = {
            "code": 200,
            "message": "Update user ok",
            "data": {}
        }

        reqParaJson = request.get_json()
        log.debug("reqParaJson=%s", reqParaJson)

        if not reqParaJson:
            return genRespFailDict(BadRequest.code, "Invalid input parameters")

        if ("id" not in reqParaJson) or (not reqParaJson["id"]):
            return genRespFailDict(BadRequest.code, "Invalid user id for empty")

        userIdStr = reqParaJson["id"]
        userId = int(userIdStr)

        existedUserSql = "SELECT * FROM `user` WHERE id = %d" % userId
        log.debug("existedUserSql=%s", existedUserSql)
        existedUserOk, resultDict = sqlConn.executeSql(existedUserSql)
        log.debug("%s -> %s, %s", existedUserSql, existedUserOk, resultDict)
        if (not existedUserOk) or (not resultDict["data"]):
            return genRespFailDict(NotFound.code, "Can not found user from id %s" % userId)

        # existedUser = resultDict["data"][0]
        # log.debug("existedUser=%s", existedUser)

        keyValueDictList = []

        if "phone" in reqParaJson:
            inputPhone = reqParaJson["phone"]

            if not inputPhone:
                return genRespFailDict(BadRequest.code, "Empty phone number")

            # duplicated bind phone notice
            existedPhoneUserSql = "SELECT * FROM `user` WHERE `phone` = '%s'" % inputPhone
            existedPhoneUserOk, resultDict = sqlConn.executeSql(existedPhoneUserSql)
            log.debug("%s -> %s, %s", existedUserSql, existedPhoneUserOk, resultDict)
            if existedPhoneUserOk and resultDict["data"]:
                existedPhoneUser = resultDict["data"][0]
                log.debug("existedPhoneUser=%s", existedPhoneUser)
                if existedPhoneUser:
                    if existedPhoneUser["id"] != userId:
                        return genRespFailDict(BadRequest.code, "Your phone %d has bind by others" % inputPhone)

            phoneKeyValueDict = {
                "key": "phone",
                "format": "'%s'",
                "value": inputPhone
            }
            keyValueDictList.append(phoneKeyValueDict)

        if "name" in reqParaJson:
            inputName = reqParaJson["name"]
            if not inputName:
                return genRespFailDict(BadRequest.code, "Empty name")

            nameKeyValueDict = {
                "key": "name",
                "format": "'%s'",
                "value": inputName
            }
            keyValueDictList.append(nameKeyValueDict)

        # generate set part sql
        keyValueStrList = []
        for eachKeyValueDict in keyValueDictList:
            eachKeyValueFormat = """`%s`=%s""" % (eachKeyValueDict["key"], eachKeyValueDict["format"]) # '`age`=%d'
            eachKeyValueStr = eachKeyValueFormat % eachKeyValueDict["value"] # '`age`=4'
            keyValueStrList.append(eachKeyValueStr)

        keyValueSql = ",".join(keyValueStrList)
        log.debug("keyValueSql=%s", keyValueSql)

        updateUserSql = "UPDATE `user` SET %s WHERE `id`=%d" % (keyValueSql, userId)
        updateUserOk, resultDict = sqlConn.executeSql(updateUserSql)
        log.debug("%s -> %s, %s", updateUserSql, updateUserOk, resultDict)
        if updateUserOk:
            resultData = resultDict["data"]
            log.debug("resultData=%s", resultData)

            # update lastActiveTime, updatedTime
            curTime = getCurUtcTime()
            log.debug("curTime=%s", curTime)
            self.updateUserTime(
                userId=userId,
                updatedTime=curTime,
                lastActiveTime=curTime)

            return self.respFullUserInfo(respDict, userId)
        else:
            return genRespFailDict(InternalServerError.code, "Update user info failed")


    def updateUserTime(self, userId, createdTime=None, updatedTime=None, lastActiveTime=None, curSqlConn=None):
        if not curSqlConn:
            curSqlConn = sqlConn

        updateTimeDictList = []

        if createdTime:
            createdTimeSql = "`createdTime`='%s'" % createdTime
            updateTimeDictList.append(createdTimeSql)

        if updatedTime:
            updatedTimeSql = "`updatedTime`='%s'" % updatedTime
            updateTimeDictList.append(updatedTimeSql)

        if lastActiveTime:
            lastActiveTimeSql = "`lastActiveTime`='%s'" % lastActiveTime
            updateTimeDictList.append(lastActiveTimeSql)

        updateTimeSql = ",".join(updateTimeDictList)
        log.debug("updateTimeSql=%s", updateTimeSql)
        updateUserTimeSql = "UPDATE `user` SET %s WHERE id=%d" % (updateTimeSql, userId)
        log.debug("updateUserTimeSql=%s", updateUserTimeSql)
        # updateUserTimeOk, resultDict = sqlConn.executeSql(updateUserTimeSql)
        updateUserTimeOk, resultDict = curSqlConn.executeSql(updateUserTimeSql)
        log.debug("%s -> %s, %s", updateUserTimeSql, updateUserTimeOk, resultDict)


    def respFullUserInfo(self, respDict, existedUserId, curSqlConn=None):
        log.debug("respFullUserInfo: respDict=%s, existedUserId=%s", respDict, existedUserId)
        if not curSqlConn:
            curSqlConn = sqlConn

        existedUserSql = "SELECT * FROM `user` WHERE id = '%s'" % existedUserId
        log.debug("existedUserSql=%s", existedUserSql)
        existedUserOk, resultDict = curSqlConn.executeSql(existedUserSql)
        log.debug("%s -> %s, %s", existedUserSql, existedUserOk, resultDict)
        if (not existedUserOk) or (not resultDict["data"]):
            return genRespFailDict(NotFound.code, "Can not found user from user id %s" % existedUserId)

        existedUser = resultDict["data"][0]
        log.debug("existedUser=%s", existedUser)

        respDict["data"] = existedUser
        return jsonify(respDict)
