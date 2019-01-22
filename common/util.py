import os
import sys
import uuid
import io
import datetime
from flask import send_file
from flask import jsonify
from bson.objectid import ObjectId
from urllib.parse import quote_plus
try:
    from PIL import Image
except:
    print("Need install pillow before use Image functions")

import base64
import json
try:
    from Crypto.Cipher import AES
except:
    print("Need install pycrypto before use Wechat functions")

import requests
import random
import string

from pymongo import MongoClient

from configparser import ConfigParser
from common import crifanMysql

### Note: most functions is copy out from my crifanLib: https://github.com/crifan/crifanLibPython


#----------------------------------------
# Current Project Functions
#----------------------------------------



#----------------------------------------
# Date time Functions
#----------------------------------------

def getCurUtcTime():
    return datetime.datetime.utcnow()

def getCurLocalTime():
    return datetime.datetime.now()

def getCurDatetimeStr(outputFormat="%Y%m%d_%H%M%S"):
    """
    get current datetime then format to string

    eg:
        20171111_220722

    :param outputFormat: datetime output format
    :return: current datetime formatted string
    """
    # curDatetime = datetime.datetime.now() # 2017-11-11 22:07:22.705101
    curDatetime = getCurLocalTime() # 2017-11-11 22:07:22.705101
    curDatetimeStr = curDatetime.strftime(format=outputFormat) #'20171111_220722'
    return curDatetimeStr

#----------------------------------------
# Flask Functions
#----------------------------------------

def sendFile(fileBytes, contentType, outputFilename, asAttachment=True):
    """
        flask return downloadable file or file's binary stream data
            example url: http://127.0.0.1:34800/audio/5c1c631c127588257d568eba/3569.mp3
    :param fileBytes:  file binary bytes
    :param contentType: MIME content type, eg: audio/mpeg
    :param outputFilename: output filename, eg: 3569.mp3
    :param asAttachment: True to return downloable file with filename, False to return binary stream file data
    :return: Flask response
    """
    """Flask API use this to send out file (to browser, browser can directly download file)"""
    # print("sendFile: len(fileBytes)=%s, contentType=%s, outputFilename=%s" % (len(fileBytes), contentType, outputFilename))
    # return send_file(
    #     io.BytesIO(fileBytes),
    #     mimetype=contentType,
    #     as_attachment=asAttachment,
    #     attachment_filename=outputFilename
    # )
    fileLength = len(fileBytes)
    responseFile = send_file(
        io.BytesIO(fileBytes),
        mimetype=contentType,
        as_attachment=asAttachment,
        attachment_filename=outputFilename
    )
    # add Content-Length to support miniprogram iOS background play audio works, not error: 10003
    responseFile.headers["Content-Length"] = fileLength
    return responseFile



def getGridfsFile(curGridfs, fileId, fileName=None, filterDataFunc=None, asAttachment=True):
    """
        generate downloadable gridfs file
    :param curGridfs: current gridfs collection
    :param fileId: mongodb gridfs file id
    :param fileName: filename
    :param filterDataFunc: before return file, filter data, such as reduce image size
    :return:
        gridfs file, support api caller(browser) to download file
    """
    print("getGridfsFile: curGridfs=%s, fileId=%s, fileName=%s, filterDataFunc=%s" %
          (curGridfs, fileId, fileName, filterDataFunc))
    # curGridfs=<gridfs.GridFS object at 0x104c5d748>, fileId=5c1c6322127588257d56935e, fileName=vedio game.png, filterDataFunc=<function compressImageSize at 0x104f6e2f0>

    fileIdObj = ObjectId(fileId)
    print("fileIdObj=%s" % fileIdObj)
    if not curGridfs.exists({"_id": fileIdObj}):
        respDict = {
            "code": 404,
            "message": "Not found gridfs file from id %s" % fileId,
            "data": {}
        }
        return jsonify(respDict)

    fileObj = curGridfs.get(fileIdObj)
    print("fileObj=%s, filename=%s, chunkSize=%s, length=%s, contentType=%s" %
          (fileObj, fileObj.filename, fileObj.chunk_size, fileObj.length, fileObj.content_type))
    print("lengthInMB=%.2f MB" % float(fileObj.length / (1024 * 1024)))

    fileBytes = fileObj.read()
    print("len(fileBytes)=%s" % len(fileBytes))

    if filterDataFunc:
        fileBytes = filterDataFunc(fileBytes)
        print("after process: len(fileBytes)=%s" % len(fileBytes))

    outputFilename = fileObj.filename
    if fileName:
        outputFilename = fileName
    print("outputFilename=%s" % outputFilename)

    return sendFile(fileBytes, fileObj.content_type, outputFilename, asAttachment=asAttachment)


def genRespFailDict(code = 400, message = "Unknown reason"):
    respFailJsonDict = {
        "code" : code,
        "message" : message,
    }
    # return respFailJsonDict
    return jsonify(respFailJsonDict)


#----------------------------------------
# MySQL Functions
#----------------------------------------

def getMysqlConnection(mysqlConfigDict):
    newSqlConn = crifanMysql.MysqlDb(config=mysqlConfigDict)
    #<util.crifanLib.crifanMysql.MysqlDb object at 0x1042ef898>
    print("newSqlConn=%s" % newSqlConn)
    newSqlConn.isUseLog = False
    print("newSqlConn.isUseLog=%s" % newSqlConn.isUseLog)
    return newSqlConn

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
        print(mongodbUri)

        if authSource:
            mongodbUri = mongodbUri + ("/%s" % authSource)
            print("mongodbUri=%s" % mongodbUri)

        if authMechanism:
            mongodbUri = mongodbUri + ("?authMechanism=%s" % authMechanism)
            print("mongodbUri=%s" % mongodbUri)

    print("return mongodbUri=%s" % mongodbUri)
    #mongodb://username:quoted_password@host:port/authSource?authMechanism=authMechanism
    #mongodb://localhost:27017

    return mongodbUri


#----------------------------------------
# File Functions
#----------------------------------------

def isFileObject(fileObj):
    """"check is file like object or not"""
    if sys.version_info[0] == 2:
        return isinstance(fileObj, file)
    else:
        # for python 3:
        # has read() method for:
        # io.IOBase
        # io.BytesIO
        # io.StringIO
        # io.RawIOBase
        return hasattr(fileObj, 'read')


#----------------------------------------
# Image Functions
#----------------------------------------

def resizeImage(inputImage,
                newSize,
                resample=Image.BICUBIC, # Image.LANCZOS,
                outputFormat=None,
                outputImageFile=None
                ):
    """
        resize input image
        resize normally means become smaller, reduce size
    :param inputImage: image file object(fp) / filename / binary bytes
    :param newSize: (width, height)
    :param resample: PIL.Image.NEAREST, PIL.Image.BILINEAR, PIL.Image.BICUBIC, or PIL.Image.LANCZOS
        https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.thumbnail
    :param outputFormat: PNG/JPEG/BMP/GIF/TIFF/WebP/..., more refer:
        https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
        if input image is filename with suffix, can omit this -> will infer from filename suffix
    :param outputImageFile: output image file filename
    :return:
        input image file filename: output resized image to outputImageFile
        input image binary bytes: resized image binary bytes
    """
    openableImage = None
    if isinstance(inputImage, str):
        openableImage = inputImage
    elif isFileObject(inputImage):
        openableImage = inputImage
    elif isinstance(inputImage, bytes):
        inputImageLen = len(inputImage)
        openableImage = io.BytesIO(inputImage)

    imageFile = Image.open(openableImage) # <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=3543x3543 at 0x1065F7A20>
    imageFile.thumbnail(newSize, resample)
    if outputImageFile:
        # save to file
        imageFile.save(outputImageFile)
        imageFile.close()
    else:
        # save and return binary byte
        imageOutput = io.BytesIO()
        # imageFile.save(imageOutput)
        outputImageFormat = None
        if outputFormat:
            outputImageFormat = outputFormat
        elif imageFile.format:
            outputImageFormat = imageFile.format
        imageFile.save(imageOutput, outputImageFormat)
        imageFile.close()
        compressedImageBytes = imageOutput.getvalue()
        compressedImageLen = len(compressedImageBytes)
        compressRatio = float(compressedImageLen)/float(inputImageLen)
        print("resizeImage: %s -> %s, resize ratio: %d%%" % (inputImageLen, compressedImageLen, int(compressRatio * 100)))
        return compressedImageBytes



#----------------------------------------
# Wechat Functions
#----------------------------------------

class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decriptedData = cipher.decrypt(encryptedData)

        unpadedData = self._unpad(decriptedData)

        decrypted = json.loads(unpadedData)

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


def decryptWechatInfo(appId, sessionKey, encryptedData, iv):
    """
        decrypt wechat info, return from https://developers.weixin.qq.com/miniprogram/dev/api/wx.getUserInfo.html
    """
    cryptObj = WXBizDataCrypt(appId, sessionKey)
    decryptedInfo = cryptObj.decrypt(encryptedData, iv)
    return decryptedInfo

def wechatGetAccessToken(appId, secret, grantType="client_credential"):
    # https://developers.weixin.qq.com/miniprogram/dev/api/getAccessToken.html
    # GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
    reqParams = {
        "grant_type": grantType,
        "appid": appId,
        "secret": secret,
    }
    getTokenUrl = "https://api.weixin.qq.com/cgi-bin/token"
    respInfo = requests.get(getTokenUrl, params=reqParams)
    respJson = respInfo.json()
    # normal: {'access_token': '17_O59-zPa3J3gr6Nn6KxdC2tcy-ca8UVbXTzwI2BGqeVnJI4hunhxbibMN-Uq_6B9jXU9hniHF2awQAjl_MsElQm6vSk2LTlQ1_HdlerlrH8Y_z5xk7apOsK1oi2YUnpWEuf_nsWRiGWUAttexXKPcAHAANS', 'expires_in': 7200}
    return respJson

#----------------------------------------
# Math Functions
#----------------------------------------

def genRandomStr(choiceStr, length):
    """random number and string"""
    randomStr = ''.join([random.choice(choiceStr) for _ in range(length)])
    return randomStr


def genRandomDigit(length):
    randomDigits = genRandomStr(string.digits, length=length)
    return randomDigits


def generateUUID(prefix = ""):
    generatedUuid4 = uuid.uuid4()
    generatedUuid4Str = str(generatedUuid4)
    newUuid = prefix + generatedUuid4Str
    return newUuid

#----------------------------------------
# Other Functions
#----------------------------------------
