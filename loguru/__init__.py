class DummyLogger:
    def debug(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def exception(self, *args, **kwargs): pass
    def remove(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass
    def critical(self, *args, **kwargs): pass
    def trace(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): pass

logger = DummyLogger()
