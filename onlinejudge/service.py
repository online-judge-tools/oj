# Python Version: 3.x

class Service(object):
    def login(self, get_credentials, session=None):
        raise NotImplementedError
    def get_url(self):
        raise NotImplementedError
    def get_name(self):
        raise NotImplementedError
    @classmethod
    def from_url(self, s):
        pass
