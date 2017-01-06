#!/usr/bin/env python3

class OnlineJudge(object):
    def download(self, session=None):
        raise NotImplementedError
    def submit(self, code, language=None, filename=None, session=None):
        raise NotImplementedError
    @classmethod
    def from_url(self, s):
        pass

    def get_url(self):
        raise NotImplementedError
    def login(self, get_credentials, session=None):  # TODO: Should this method exists here? Contest class is needed.
        raise NotImplementedError


list = []
def from_url(s):
    for cls in list:
        it = cls.from_url(s)
        if it is not None:
            return it
