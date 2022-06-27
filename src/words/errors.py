
class Error(Exception):
    def __init__(self, msg):
        self.message = msg


class ImplementError(Error):
    def __init__(self, fct):
        self.message = "\"{}\" non implémenté".format(fct)
    pass
