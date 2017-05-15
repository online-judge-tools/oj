# Python Version: 3.x

class Problem(object):
    def download(self, session=None):
        raise NotImplementedError
    def submit(self, code, language, session=None):
        raise NotImplementedError
    def get_language_dict(self, session=None): # => dict like: { language_id: { 'description': str } }
        raise NotImplementedError
    def get_url(self):
        raise NotImplementedError
    def get_service(self):
        raise NotImplementedError
    @classmethod
    def from_url(self, s):
        pass
