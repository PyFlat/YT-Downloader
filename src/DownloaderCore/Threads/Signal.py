class Signal():
    def __init__(self, *types):
        self.__functions = []
    def connect(self, fn : callable):
        if not fn in self.__functions:
            self.__functions.append(fn)
    def disconnect(self, fn : callable):
        if fn in self.__functions:
            self.__functions.remove(fn)
    def emit(self, *args):
        for fn in self.__functions:
            fn.__call__(*args)