REQ = 0
REP = 1
PUB = 2
SUB = 3
PUSH = 4
PULL = 5
DEALER = 6
ROUTER = 7
PAIR = 8
RCVTIMEO = 9
SNDTIMEO = 10
SUBSCRIBE = 11
UNSUBSCRIBE = 12

class Context:
    def socket(self, *args, **kwargs):
        return DummySocket()

class DummySocket:
    def __init__(self):
        pass
    def connect(self, *args, **kwargs):
        pass
    def send(self, *args, **kwargs):
        pass
    def recv(self, *args, **kwargs):
        return b''
    def close(self):
        pass
    def setsockopt(self, *args, **kwargs):
        pass
    def setsockopt_string(self, *args, **kwargs):
        pass
