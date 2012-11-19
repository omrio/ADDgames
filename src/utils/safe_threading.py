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

