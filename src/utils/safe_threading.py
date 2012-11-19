__author__ = 'daniel ben zvi'
from os import getpid
import sys
from threading import Lock as OriginalLock
from threading import RLock as OriginalRLock

def monkeyPatch():
    """
    Patches the logging module with a new lock creation method that uses SafeRLock instead of the original RLock
    logging is known to have deadlock issues when mixing threads and forks
    If a thread acquires the logging lock while a fork is being performed,
    the child will infinitely wait for the lock to be released by a non-existing thread.

    This method should be called at the beginning of the main module.
    """
    logging = sys.modules.get('logging')

    if logging and getattr(logging, '_safe_threading_monkeypatch', None):
        return

    if logging:
        print 'Logging module already imported while monkey patching safe_threading'

    import logging

    if logging.getLogger().handlers:
        raise Exception('Logging handlers already registered.')

    def safeCreateLock(self):
        self.lock = SafeRLock()

    logging.Handler.createLock = safeCreateLock
    logging._lock = SafeRLock()


    logging._safe_threading_monkeypatch = True

class SafeLock(object):
    """
    Safe lock
    This lock wraps the original lock with one big difference
    If our pid changed (due to a fork), we will replace the underlying lock instance with a new one
    This makes sure that child processes will not be left with infinitely locked mutexes and deadlock forever.

    Underlying lock instance is created using _genInstance(),
    which should be subclassed for different lock objects that implement the same interface.
    """
    def __init__(self):
        self.__pid = getpid()
        self._instance = self._genInstance()

    def _genInstance(self):
        return OriginalLock()

    def __checkPid(self):
        if self.__pid != getpid():
            self.__pid = getpid()
            self._instance = self._genInstance()

    def acquire(self, *args, **kwargs):
        self.__checkPid()
        return self._instance.acquire(*args, **kwargs)

    def release(self):
        return self._instance.release()

    def locked(self):
        return self._instance.locked()

    def __getattr__(self, item):
        print self._instance, item
        attr = getattr(self._instance, item)

        if callable(attr):
            return lambda *a, **kw: getattr(self._instance, item)(*a, **kw)

        return attr

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._instance.__exit__(exc_type, exc_val, exc_tb)

    def __enter__(self):
        self.__checkPid()
        return self._instance.__enter__()

    def __str__(self):
        return str(self._instance)

    def __repr__(self):
        return repr(self._instance)

    def __del__(self):
        del self._instance

class SafeRLock(SafeLock):
    """
    Inherits from SafeLock
    Implements _genInstance differently to produce an RLock instance.
    """
    def __init__(self):
        SafeLock.__init__(self)

    def _genInstance(self):
        return OriginalRLock()


# Can wrap everything.
class SafeProxy(object):
    """
    This special proxy can wrap any callable and replace the underlying instance if our pid changed (due to a fork)
    """
    def __init__(self, cls, instance=None, args=None, kwargs=None):
        self.__dict__['__cls'] = cls
        self.__dict__['__pid'] = getpid()
        self.__dict__['__args'] = args
        self.__dict__['__kwargs'] = kwargs
        self.__dict__['__instance'] = instance

    def __call__(self, *args, **kwargs):
        if not self.__dict__['__instance']:
            # The factory method
            return SafeProxy(self.__dict__['__cls'], self.__dict__['__cls'](*args, **kwargs), args, kwargs)
        else:
            return self.__dict__['__instance'](*args, **kwargs)
    
    def __checkPid(self):
        if getpid() != self.__dict__['__pid']:
            self.__dict__['__pid'] = getpid()
            self.__dict__['__instance'] = self.__dict__['__cls'](*self.__dict__['__args'], **self.__dict__['__kwargs'])

    def __getattr__(self, item):
        self.__checkPid()

        target = self.__dict__['__instance'] if self.__dict__.get('__instance') else self.__dict__['__cls']

        attr = getattr(target, item)

        if callable(attr):
            return lambda *args, **kwargs: getattr(self.__dict__['__instance'], item)(*args, **kwargs)

        return attr


    def __setattr__(self, key, value):
        self.__checkPid()

        target = self.__dict__['__instance'] if self.__dict__.get('__instance') else self.__dict__['__cls']

        return setattr(target, key, value)

    def __str__(self):
        self.__checkPid()

        target = self.__dict__['__instance'] if self.__dict__.get('__instance') else self.__dict__['__cls']

        return str(target)

    def __repr__(self):
        self.__checkPid()

        target = self.__dict__['__instance'] if self.__dict__.get('__instance') else self.__dict__['__cls']

        return reprt(target)

    def __del__(self):
        self.__checkPid()

        if self.__dict__.get('__instance'):
            if getattr(self.__dict__['__instance'], '__del__', None):
                return self.__dict__['__instance'].__del__()

    def __enter__(self):
        self.__checkPid()

        if self.__dict__.get('__instance'):
            return self.__dict__['__instance'].__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Does not check pid!

        if self.__dict__.get('__instance'):
            return self.__dict__['__instance'].__exit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def inject(module, property, cls):
        setattr(module, property, SafeProxy(cls))