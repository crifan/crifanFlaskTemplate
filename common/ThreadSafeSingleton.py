import functools
import threading

thread_lock = threading.Lock()
print("ThreadSafeSingleton: thread_lock=%s" % thread_lock)

# refer: https://stackoverflow.com/questions/50566934/why-is-this-singleton-implementation-not-thread-safe

def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        print("synchronized: wrapper: f=%s, lock=%s" % (f, lock))
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            print("functools.wraps: args=%s, kw=%s" % (args, kw))
            with lock:
                return f(*args, **kw)
        print("inner_wrapper%s" % inner_wrapper)
        return inner_wrapper
    return wrapper


# class Singleton(type):
class ThreadSafeSingleton(type):
    _instances = {}

    @synchronized(thread_lock)
    def __call__(cls, *args, **kwargs):
        print("synchronized __call__: cls=%s, args=%s, kwargs=%s" % (cls, args, kwargs))
        print("cls._instances=%s" % cls._instances)
        if cls not in cls._instances:
            # cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)
            print("after added _instances: cls._instances=%s" % cls._instances)
        return cls._instances[cls]