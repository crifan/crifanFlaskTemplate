# -*- coding: utf-8 -*-

import os
import re
from urllib.parse import quote_plus

import mime

# import pymongo
from pymongo import MongoClient
# import gridfs
from gridfs import GridFS
# from bson.objectid import ObjectId
import codecs
import csv

#----------------------------------------
# Configuration & Constant
#----------------------------------------

MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_ISUSEAUTH = False
MONGODB_USERNAME = None
MONGODB_PASSWORD = None
MONGODB_AUTH_SOURCE = None
MONGODB_AUTH_MECHANISM = None


MONGODB_DB_FLASK_TEMPLATE = "flask_template"
MONGODB_FLASK_TEMPLATE_COLLECTION_CAR = "car"

CURRENT_FOLDER = os.path.dirname(__file__)
CAR_FOLDER = os.path.abspath(os.path.join("..", "..", "assets", "car"))
CAR_FILENAME = "汽车之家品牌车系车型数据-25564条 180429 utf8.csv"
CAR_FULL_NAME = os.path.join(CAR_FOLDER, CAR_FILENAME)

#----------------------------------------
# File Functions
#----------------------------------------

def getBasename(fullFilename):
    """
    get base filename

    Examples:
        xxx.exe          -> xxx.exe
        xxx              -> xxx
        Mac/Linux:
           your/path/xxx.py -> xxx.py
        Windows:
           your\path\\xxx.py -> xxx.py
    """

    return os.path.basename(fullFilename)


def getFileSuffix(filename):
    """
        get file suffix from file name
        no dot/period, no space/newline, makesure lower case

        "xxx.mp3" -> "mp3"
        "xxx.pdf" -> "pdf"
        "xxx.mp3 " -> "mp3"
        "xxx.JPg" -> "jpg"

    :param filename:
    :return:
    """
    fileSuffix = ""

    if filename:
        name, extension = os.path.splitext(filename)
        fileSuffix = extension # .mp3

    if fileSuffix:
        # remove leading dot/period
        fileSuffix = fileSuffix[1:] # mp3

    if fileSuffix:
        # remove ending newline or space
        fileSuffix = fileSuffix.strip()

    if fileSuffix:
        # convert JPg to jpg
        fileSuffix = fileSuffix.lower()

    return fileSuffix


def getFileFolderSize(fileOrFolderPath):
  """get size for file or folder"""
  totalSize = 0

  if not os.path.exists(fileOrFolderPath):
    return totalSize

  if os.path.isfile(fileOrFolderPath):
    totalSize = os.path.getsize(fileOrFolderPath) # 5041481
    return totalSize

  if os.path.isdir(fileOrFolderPath):
    with os.scandir(fileOrFolderPath) as dirEntryList:
      for curSubEntry in dirEntryList:
        curSubEntryFullPath = os.path.join(fileOrFolderPath, curSubEntry.name)
        if curSubEntry.is_dir():
          curSubFolderSize = getFileFolderSize(curSubEntryFullPath) # 5800007
          totalSize += curSubFolderSize
        elif curSubEntry.is_file():
          curSubFileSize = os.path.getsize(curSubEntryFullPath) # 1891
          totalSize += curSubFileSize

      return totalSize


#----------------------------------------
# MongoDB Functions
#----------------------------------------

def generateMongoUri(host=None,
                port=None,
                isUseAuth=False,
                username=None,
                password=None,
                authSource=None,
                authMechanism=None):

    """"generate mongodb uri"""
    mongodbUri = ""

    if not host:
        # host = "127.0.0.0"
        host = "localhost"

    if not port:
        port = 27017

    mongodbUri = "mongodb://%s:%s" % (
        host, \
        port
    )
    # 'mongodb://localhost:27017'
    # 'mongodb://47.96.131.109:27017'

    if isUseAuth:
        mongodbUri = "mongodb://%s:%s@%s:%s" % (
            quote_plus(username), \
            quote_plus(password), \
            host, \
            port \
        )
        # print(mongodbUri)

        if authSource:
            mongodbUri = mongodbUri + ("/%s" % authSource)
            # print("mongodbUri=%s" % mongodbUri)

        if authMechanism:
            mongodbUri = mongodbUri + ("?authMechanism=%s" % authMechanism)
            # print("mongodbUri=%s" % mongodbUri)

    # print("return mongodbUri=%s" % mongodbUri)
    #mongodb://username:quoted_password@host:port/authSource?authMechanism=authMechanism
    #mongodb://localhost:27017

    return mongodbUri



#----------------------------------------
# Main
#----------------------------------------

def initMongodb():
    mongoUri = generateMongoUri(
        host=MONGODB_HOST,
        port=int(MONGODB_PORT),
        isUseAuth= MONGODB_ISUSEAUTH,
        username=MONGODB_USERNAME,
        password=MONGODB_PASSWORD,
        authSource=MONGODB_AUTH_SOURCE,
        authMechanism=MONGODB_AUTH_MECHANISM,
    )
    mongoClient = MongoClient(mongoUri)
    return mongoClient

def getMongoCollection(mongoClient):
    dbFlaskTemplate = mongoClient[MONGODB_DB_FLASK_TEMPLATE]
    collectionCar = dbFlaskTemplate[MONGODB_FLASK_TEMPLATE_COLLECTION_CAR]
    return collectionCar

def saveCarToMongodb():
    mongoClient = initMongodb()
    collectionCar = getMongoCollection(mongoClient)

    curNum = 1
    with codecs.open(CAR_FULL_NAME, "r", encoding="utf-8") as carFp:
        csvReader = csv.reader(carFp)
        csvHeaders = next(csvReader) # <class 'list'>: ['url', '品牌', '子品牌', '车型', '车系']
        print("csvHeaders=%s" % csvHeaders)
        for eachRow in csvReader:
            # print("eachRow=%s" % eachRow)
            # eachRow=['https://car.autohome.com.cn/pic/series-s19501/3548.html#pvareaid=2042220', 'Elemental', 'Elemental', '2014款 基本型', 'Elemental RP1']
            carUrl = eachRow[0]
            carBrand = eachRow[1]
            carSubBrand = eachRow[2]
            carModel = eachRow[3]
            carSeries = eachRow[4]
            carDict = {
                "url": carUrl,
                "brand": carBrand,
                "subBrand": carSubBrand,
                "model": carModel,
                "series": carSeries
            }
            insertedResult = collectionCar.insert_one(carDict)
            # print("insertedResult=%s" % insertedResult)
            if insertedResult:
                newId = insertedResult.inserted_id
                print("[%5d] newId=%s <- %s" % (curNum, newId, eachRow))

            curNum += 1


if __name__ == "__main__":
    saveCarToMongodb()