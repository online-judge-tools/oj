# Python Version: 3.x

class Problem(object):
    def download(self, session=None):  # => [ { 'input': { 'data': str, 'name': str }, 'output': { ... } } ]
        raise NotImplementedError
    def submit(self, code, language, session=None):
        raise NotImplementedError
    def get_language_dict(self, session=None):  # => { language_id: { 'description': str } }
        raise NotImplementedError
    def get_url(self):
        raise NotImplementedError
    def get_service(self):
        raise NotImplementedError
    def get_standings(self, session=None):  # => ( [ 'column1', 'column2', ... ], [ { 'column1': data1, ... } ... ] )
        raise NotImplementedError
    @classmethod
    def from_url(self, s):
        pass
