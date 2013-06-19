import os

class reify(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class USBTMC(object):

    def __init__(self, device):
        self.f = os.open(device, os.O_RDWR)

    def read(self, length=4000):
        return os.read(self.f, length)

    def write(self, data):
        os.write(self.f, data)

    @reify
    def name(self):
        self.write("*IDN?")
        return self.read(300)

    def reset(self):
        self.write("*RST")

