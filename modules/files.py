from werkzeug.exceptions import *
from urllib.parse import unquote
from flask import request
from flask_restful import Resource
from flask import g
import mime
import io

from common.FlaskLogSingleton import log
from common.util import resizeImage, getGridfsFile, getCurDatetimeStr, genRespFailDict
from conf.app import settings


mongoDbFlaskTemplateGridfsFiles = g.mongoDbFlaskTemplateGridfsFiles


#----------------------------------------
# Util Functions
#----------------------------------------

def compressImageSize(fileBytes):
    return resizeImage(fileBytes, settings.IMAGE_COMPRESS_SIZE)

def respUploadedGridfsFile(request, respDict, curGridfs):
    curMimeType = ""
    requestHeaders = request.headers
    if "filename" in requestHeaders:
        filename = requestHeaders["filename"] # '%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20181%20228160748.jpg'
        filename = unquote(filename) # '微信图片_20181 228160748.jpg'
        curMimeType = mime.Types.of(filename)[0].content_type
    else:
        filename = getCurDatetimeStr()

    fileBinData = request.stream.read()
    fileLikeObj = io.BytesIO(fileBinData)
    log.debug("filename=%s, curMimeType=%s, len(fileBinData)=%s", filename, curMimeType, len(fileBinData))

    newFileObjId = curGridfs.put(
        fileLikeObj,
        filename=filename,
        content_type=curMimeType)

    if newFileObjId:
        readOutFile = curGridfs.get(newFileObjId)
        respDict["data"] = {
            "_id": str(readOutFile._id),
            "filename": readOutFile.filename,
            "contentType": readOutFile.contentType,
            "length": readOutFile.length,
            "uploadDate": str(readOutFile.uploadDate),
            "md5": readOutFile.md5,
        }
        return respDict
    else:
        return genRespFailDict(InternalServerError.code, "Fail to create gridfs file %s" % filename)


#----------------------------------------
# Flask API Functions
#----------------------------------------

class FileFlaskTemplateFilesAPI(Resource):

    def post(self):
        log.info("FileFlaskTemplateFilesAPI POST")

        respDict = {
            "code": 200,
            "message": "Create new gridfs file ok",
            "data": {}
        }

        return respUploadedGridfsFile(request, respDict, mongoDbFlaskTemplateGridfsFiles)


    def get(self, fileId, fileName=None):
        # 'http://10.108.133.251:34800/file/evaluation/image/5c32f6ae12758802476f7cd2/hide%20in%20the%20box.png'
        # 'http://10.108.133.251:34800/file/storybook/audio/5c482cb6dc54867a9eff34a9/All%20By%20Myself.mp3'
        log.info("FileFlaskTemplateFilesAPI GET: fileId=%s, fileName=%s", fileId, fileName)
        range = None
        if "Range" in request.headers:
            range = request.headers["Range"]
            log.debug("range=%s", range)
        # return getFile(MongoFileType.STORYBOOK_AUDIO.value, fileId, fileName, range)

        # def getFile(fileType, fileId, fileName=None, range=None):
        # log.info("getFile: fileType=%s, fileId=%s, fileName=%s", fileType, fileId, fileName)

        curGridfs = mongoDbFlaskTemplateGridfsFiles
        asAttachment = settings.GRIDFS_FILE_AS_ATTACHMENT
        return getGridfsFile(curGridfs, fileId, fileName, asAttachment=asAttachment, range=range)
        # Note: if know current file is image, and expect return compressed image, can use:
        # return getGridfsFile(curGridfs, fileId, fileName, compressImageSize, asAttachment=asAttachment, range=range)


# Note: NO need following code to serve static file
#   but only need init makesure static_folder correct when init Flask in factory.py
# class StaticFilesAPI(Resource):
#     def get(self, fileName=None):
#         log.info("StaticFilesAPI: fileName=%s", fileName)
#         return send_from_directory(settings.FILE_STATIC_FOLDER, fileName, as_attachment=True)
