import multiprocessing
import os
import sys
# sys.path.append(".")
# from config import BaseConfig

curPath = os.path.dirname(os.path.abspath(__file__))
# print("curPath=%s" % curPath)
confPath = os.path.join(curPath, "..")
# print("confPath=%s" % confPath)
sys.path.append(confPath)
from conf.app import settings
# print("settings=%s" % settings)

appRootPath = os.path.join(confPath, "..")
# print("appRootPath=%s" % appRootPath)
flaskHost = settings.FLASK_HOST
flaskPort = settings.FLASK_PORT
# print("flaskHost=%s, flaskPort=%s" % (flaskHost, flaskPort))


reload = True                                   #当代码改变时自动重启服务
bind = ("%s:%s" % (flaskHost, flaskPort))
backlog = 512                                   #监听队列
chdir = appRootPath                             #gunicorn要切换到的目的工作目录
timeout = 30                                    #超时

worker_class = 'sync'                           #默认的是sync模式
workers = multiprocessing.cpu_count() * 2 + 1   #进程数

# http://docs.gunicorn.org/en/stable/settings.html#threads
threads = 2                                     #指定每个进程开启的线程数

# # http://docs.gunicorn.org/en/stable/settings.html#worker-class
# # Note: change to use gevent, 1 worker but multiple threads to make singleton workable for data share
# # such as ms tts token MsTtsTokenSingleton
# worker_class = 'gevent'
# workers = 1   #进程数
# # http://docs.gunicorn.org/en/stable/settings.html#max-requests
# # worker_connections = 2000 # 默认是1000
# worker_connections = 10000
# # http://docs.gunicorn.org/en/stable/settings.html#max-requests
# max_requests = 0

loglevel = 'debug'                               #日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
#http://docs.gunicorn.org/en/stable/settings.html#access-log-format
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'    #设置gunicorn访问日志格式，错误日志无法设置
accesslog = appRootPath + "/logs/%s/gunicorn_access.log" % (settings.FLASK_ENV)      #访问日志文件
errorlog  = appRootPath + "/logs/%s/gunicorn_error.log" % (settings.FLASK_ENV)       #错误日志文件
