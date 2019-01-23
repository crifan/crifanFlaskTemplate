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

#----------------------------------------
# Configuration
#----------------------------------------

isDeleteBeforeAddMongodbFile = True

MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_ISUSEAUTH = False
MONGODB_USERNAME = None
MONGODB_PASSWORD = None
MONGODB_AUTH_SOURCE = None
MONGODB_AUTH_MECHANISM = None


MONGODB_DB_FLASK_TEMPLATE = "flask_template"
MONGODB_COLLECTION_FILES = "files"

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

def getMongoGridfsCollection(mongoClient):
    dbFlaskTemplate = mongoClient[MONGODB_DB_FLASK_TEMPLATE]
    collectionFs = GridFS(dbFlaskTemplate, MONGODB_COLLECTION_FILES)
    return collectionFs

def saveSingleFileToMongodb(collectionFs, curFullFilename):
    metadataDict = {
        "fileInfo": {}
    }

    curFilename = getBasename(curFullFilename)
    metadataDict["fileInfo"]["name"] = curFilename

    fileSize = getFileFolderSize(curFullFilename)
    metadataDict["fileInfo"]["size"] = fileSize

    fileSuffix = getFileSuffix(curFullFilename)
    metadataDict["fileInfo"]["suffix"] = fileSuffix

    # extract MIME
    curFileMimeType = mime.Types.of(curFilename)[0].content_type
    # 'audio/mpeg', 'application/pdf', 'image/png', 'image/jpeg'
    metadataDict["fileInfo"]["contentType"] = curFileMimeType

    isAudio = False
    if re.match("^audio/.+", curFileMimeType):
        isAudio = True
    metadataDict["fileInfo"]["isAudio"] = isAudio

    isImage = False
    if re.match("^image/.+", curFileMimeType):
        isImage = True
    metadataDict["fileInfo"]["isImage"] = isImage

    # with open(curFullFilename) as curFp:
    with open(curFullFilename, mode="rb") as curFp:
        curFileObjectId = collectionFs.put(
            curFp,
            filename=curFilename,
            content_type=curFileMimeType,
            metadata=metadataDict)

        readOutFile = collectionFs.get(curFileObjectId)
        fileMetadata = readOutFile.metadata
        print("fileMetadata=%s" % fileMetadata)

def processFolder(collectionFs, curFolerPath):
    ignoreFileList = [
        ".DS_Store"
    ]
    with os.scandir(curFolerPath) as dirEntryList:
        for curDirEntry in dirEntryList:
          if curDirEntry.is_file():
            if curDirEntry.name in ignoreFileList:
                continue
            curFullPath = curDirEntry.path
            saveSingleFileToMongodb(collectionFs, curFullPath)

def mongodbGridfsDeleteAll(collectionFs):
    curNum = 0
    foundAllFilesCursor = collectionFs.find()
    for curIdx, eachFile in enumerate(foundAllFilesCursor):
        curNum = curIdx + 1
        fileObjectIdToDelete = eachFile._id
        filename = eachFile.filename
        collectionFs.delete(fileObjectIdToDelete)
        print("[%4d] deleted file id=%s, filename=%s" % (curNum, fileObjectIdToDelete, filename))
    print("------ Total deleted [%d] files" % curNum)

def saveFileToMongodb():
    mongoClient = initMongodb()
    collectionFs = getMongoGridfsCollection(mongoClient)

    if isDeleteBeforeAddMongodbFile:
        mongodbGridfsDeleteAll(collectionFs)

    currentFilePath = os.path.abspath(__file__)
    currentPath = os.path.dirname(currentFilePath)
    projectRootPath = os.path.abspath(os.path.join(currentPath, "..", ".."))
    assetsRootPath = os.path.join(projectRootPath, "assets")
    audiosPath = os.path.join(assetsRootPath, "audios")
    imagesPath = os.path.join(assetsRootPath, "images")
    processFolder(collectionFs, audiosPath)
    processFolder(collectionFs, imagesPath)

if __name__ == "__main__":
    saveFileToMongodb()