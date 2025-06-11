class Response:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.headers = {'content-type': 'application/json'}
        self.text = ''
    def json(self):
        return self._json
    def raise_for_status(self):
        pass

class Session:
    def __init__(self):
        pass
    def request(self, *args, **kwargs):
        return Response()
    def close(self):
        pass
from . import exceptions
