class Struct:
    """
    Thanks, Eli Bendersky
    http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    """
    def __init__(self, entries):
        self.__dict__.update(entries)
