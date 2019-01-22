from invoke import task
from fabric import Connection
from patchwork.transfers import rsync
import os

RemoteHost = 'production_server_ip'
RemoteUser = 'root'
RemotePathRoot = '/ProjectRootPath'

def seperatorLine(seperatorChar='-', count=80):
    print(seperatorChar * count)

def fabLoadedPath():
    from fabric.main import program
    return program.collection.loaded_from

@task
def upload(context):
    # print("upload: context=%s", context)
    seperatorLine()
    fabFilePath = fabLoadedPath()
    # print("fabFilePath=%s" % fabFilePath)
    localProjectRootPath = os.path.join(fabFilePath, "..")
    # print("localProjectRootPath=%s" % localProjectRootPath)
    # seperatorLine()
    # print("Local environment:")
    # context.run("uname -a")
    # context.run("pwd")
    # context.run("ls -lha")
    # seperatorLine()
    remoteConn = Connection(host=RemoteHost, user=RemoteUser)
    # print(remoteConn)
    # seperatorLine()
    # print("Remote Server:")
    # remoteConn.run('uname -a')
    # remoteConn.run('pwd')
    # print("remote path: %s" % RemotePathRoot)
    # remoteConn.run('ls -lha %s' % (RemotePathRoot))
    # remoteConn.run('cd %s && pwd && ls -lha' % RemotePathRoot)
    # putFileResult = remoteConn.put('fabfile.py', remote=RemotePathRoot)
    # print("Uploaded {0.local} to {0.remote}".format(putFileResult))

    syncSource = localProjectRootPath
    syncTarget = RemotePathRoot
    # syncExclude = [".DS_Store", "data/", "processData/", "*.log", "*.pyc", "__pycache__"]
    syncExclude = [
        ".DS_Store", ".git/", ".idea/", "*.pyc", "__pycache__",
        "dump.rdb", "debug/", "logs/", "runtime/", "tmp/"]
    syncResp = rsync(
        remoteConn,
        source=syncSource,
        target=syncTarget,
        # Note: be careful to add `delete`, to void to delete unexpected files
        # delete=True,
        exclude=syncExclude)
    seperatorLine()
    # print("Sync lcoal %s to remote %s while exclude %s -> return %s" %
    #       (syncSource, syncTarget, syncExclude, syncResp))
    print("Sync lcoal:\n%s\nto remote:\n%s\nwhile exclude:\n%s\n-> return:\n%s" % (syncSource, syncTarget, syncExclude, syncResp))
