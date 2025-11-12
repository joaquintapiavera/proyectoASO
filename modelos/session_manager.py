import os

class RootSession:
    _instance = None

    def __init__(self):
        self.is_root = (hasattr(os, "geteuid") and os.geteuid() == 0)
        self.authenticated = self.is_root
        self.password = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = RootSession()
        return cls._instance

    def set_authenticated(self, password=None):
        self.authenticated = True
        self.password = password

    def clear(self):
        self.authenticated = self.is_root
        self.password = None
