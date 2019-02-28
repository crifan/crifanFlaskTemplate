from bson.objectid import ObjectId
from werkzeug.exceptions import *
from flask import jsonify
from flask import g
from flask_restful import Resource
from flask_restful import reqparse
from common.FlaskLogSingleton import log
import pymongo

from common.util import genRespFailDict
from conf.app import settings

mongoDbFlaskTemplate = g.mongoDbFlaskTemplate
collectionCar = g.mongoDbFlaskTemplateCollectionCar

sqlConn = g.sqlConn
redisStore = g.redisStore

#----------------------------------------
# Util Functions
#----------------------------------------



def filterCarDict(carDict):
    carDict["_id"] = str(carDict["_id"])
    return carDict


def respFindOneCar(findParam, respDict):
    foundCarObj = collectionCar.find_one(findParam)
    if not foundCarObj:
        return genRespFailDict(NotFound, "Can not find car from %s" % findParam)

    foundCarDict = filterCarDict(foundCarObj)
    respDict["data"] = foundCarDict
    return jsonify(respDict)

#----------------------------------------
# Flask API Functions
#----------------------------------------

class CarAPI(Resource):

    def get(self):
        log.info("CarAPI GET")

        respDict = {
            "code": 200,
            "message": "Get car ok",
            "data": {}
        }

        parser = reqparse.RequestParser()
        # parameters for get single car info
        parser.add_argument('id', type=str, help="str: car id")
        # parameters for get car list
        parser.add_argument('pageNumber', type=int, default=1, help="page number for get car list")
        parser.add_argument('pageSize', type=int, default=settings.CAR_PAGE_SIZE, help="page size for get car list")
        parser.add_argument('searchText', type=str, help="search text for get car list")

        parsedArgs = parser.parse_args()
        log.debug("parsedArgs=%s", parsedArgs)

        if not parsedArgs:
            return genRespFailDict(BadRequest, "Fail to parse input parameters")

        carId = parsedArgs["id"]

        if carId:
            findParam = None
            if carId:
                carIdObj = ObjectId(carId)
                findParam = {'_id': carIdObj}

            return respFindOneCar(findParam, respDict)
        else:
            # get car list
            pageNumber = parsedArgs["pageNumber"]
            pageSize = parsedArgs["pageSize"]
            if pageNumber < 1:
                return genRespFailDict(BadRequest.code, "Invalid pageNumber %d" % pageNumber)

            findParam = {}

            searchText = parsedArgs["searchText"]
            if searchText:
                """
                {
                  "_id": "5c779841bfaa442ee1b14f8f",
                  "url": "https://car.autohome.com.cn/pic/series-s24892/403.html#pvareaid=2042220",
                  "brand": "雷克萨斯",
                  "subBrand": "雷克萨斯",
                  "model": "2016款 200 Midnight特别限量版",
                  "series": "雷克萨斯ES"
                }
                """
                searchTextOrParamList = [
                    {"url": {"$regex": searchText, "$options": "im"}},
                    {"brand": {"$regex": searchText, "$options": "im"}},
                    {"subBrand": {"$regex": searchText, "$options": "im"}},
                    {"model": {"$regex": searchText, "$options": "im"}},
                    {"series": {"$regex": searchText, "$options": "im"}},
                ]

                searchTextAndParamList = [{ "$or": searchTextOrParamList}]
                if "$and" in findParam:
                    findParam["$and"].extend(searchTextAndParamList)
                else:
                    findParam["$and"] = searchTextAndParamList

            sortBy = "url"
            log.debug("findParam=%s", findParam)
            sortedCarsCursor = collectionCar.find(findParam).sort(sortBy, pymongo.ASCENDING)
            totalCount = sortedCarsCursor.count()
            log.debug("search car: %s -> totalCount=%s", findParam, totalCount)
            if totalCount == 0:
                respData = {}
            else:
                # Note: for debug
                # follow will cause error: pymongo.errors.InvalidOperation cannot set options after executing query
                # foundAllCars = list(sortedCarsCursor)
                # log.debug("foundAllCars=%s", foundAllCars)

                totalPageNum = int(totalCount / pageSize)
                if (totalCount % pageSize) > 0:
                    totalPageNum += 1
                if pageNumber > totalPageNum:
                    return genRespFailDict(BadRequest.code, "Current page number %d exceed max page number %d" % (pageNumber, totalPageNum))

                skipNumber = pageSize * (pageNumber - 1)
                limitedCarsCursor = sortedCarsCursor.skip(skipNumber).limit(pageSize)
                carList = list(limitedCarsCursor)
                removeObjIdList = []
                for eachCar in carList:
                    eachCar = filterCarDict(eachCar)
                    removeObjIdList.append(eachCar)

                hasPrev = False
                if pageNumber > 1:
                    hasPrev = True
                hasNext = False
                if pageNumber < totalPageNum:
                    hasNext = True

                respData = {
                    "carList": removeObjIdList,
                    "curPageNum": pageNumber,
                    "numPerPage": pageSize,
                    "totalNum": totalCount,
                    "totalPageNum": totalPageNum,
                    "hasPrev": hasPrev,
                    "hasNext": hasNext,
                }

            respDict["data"] = respData
            return jsonify(respDict)

