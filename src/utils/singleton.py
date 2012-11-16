'''
Generic singleton wrapper
Created on Sep 21, 2011

@author: dvirsky
'''
from safe_threading import SafeRLock

class Singleton(object):

    __instance = None
    # Recursive lock is needed here in case a singleton initialization causes another singleton to initialize
    __lock = SafeRLock()

    @classmethod
    def instance(cls):

        """
        @return Singleton
        """
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = cls()

        return cls.__instance

    @classmethod
    def reinstance(cls, instance):

        tmp = None
        if cls.__instance:
            tmp = cls.__instance
        cls.__instance = instance

        del tmp
