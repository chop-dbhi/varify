import logging


class NullHandler(logging.Handler):
    """
    Workaround to support Python 2.6

    NullHandler was officially added to the logging package in Python 2.7
    """
    def emit(self, record):
        pass


class MockHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }
