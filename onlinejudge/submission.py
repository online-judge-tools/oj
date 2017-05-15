# Python Version: 3.x

class Submission(object):
    def download(self, session=None):
        raise NotImplementedError
    def get_url(self):
        raise NotImplementedError
    def get_problem(self):
        raise NotImplementedError
    def get_service(self):
        raise self.get_problem().get_service()
    @classmethod
    def from_url(cls, s):
        pass

class CompatibilitySubmission(Submission):
    def __init__(self, url, problem=None):
        self.url = url
        self.problem = problem
    def get_url(self):
        return self.url
    def get_problem(self):
        return self.problem
