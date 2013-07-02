from .usbtmc import USBTMC

import numpy
import time


"""
Note that in order to get the usbtmc device world readable and writable, I added
a file: /etc/udev/rules.d/99-local.rules:

    ENV{MAJOR}=="180", ENV{MINOR}=="176", MODE="0666", NAME="oscope"

I set the name in case I later get another usbtmc device, I want to reliably
have the same device show up at the same file.  I'm no udev expert, YMMV.
"""

class Oscope(USBTMC):
    """
    Rigol DS1000 series.
    """
    timescales = [
        5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
        1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
        1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3,
        1, 2, 5, 10, 20, 50]

    def __init__(self, device='/dev/oscope'):
        super(Oscope, self).__init__(device)
        self.device = device
        self.one = Channel(self, 'CHAN1')
        self.two = Channel(self, 'CHAN2')

    def stop(self):
        """
        Stop data acquisition.
        """
        self.write(":STOP")

    def run(self):
        self.write(":RUN")
        self.write(":KEY:FORC")

    def local_mode(self):
        self.write(":KEY:FORC")

    @apply
    def timescale():
        """
        Voltage scale.
        """
        def read(self):
            self.write(":TIM:SCAL?")
            return float(self.read(20))

        def write(self, scale):
            self.write(":TIM:SCAL %0.9f" % scale)
            while self.timescale != scale:
                pass

        return property(read, write)

    @property
    def timeoffset(self):
        """
        Voltage offset.
        """
        self.write(":TIM:OFFS?")
        return float(self.read(20))


class Channel(USBTMC):

    def __init__(self, oscope, id):
        super(Channel, self).__init__(oscope.device)
        self.oscope = oscope
        self.id = id

    @property
    def voltscale(self):
        """
        Voltage scale.
        """
        self.write(":%s:SCAL?" % self.id)
        return float(self.read(20))

    @property
    def voltoffset(self):
        """
        Voltage offset.
        """
        self.write(":%s:OFFS?" % self.id)
        return float(self.read(20))

    def capture_voltage(self):
        """
        Capture screen full of data.
        """
        self.write(":WAV:POIN:MODE NOR")
        self.write(":WAV:DATA? %s" % self.id)
        raw = self.read(9000)
        data = numpy.frombuffer(raw, 'B')

        # First 10 points seem to be garbage for some reason, not sure
        # what's going on.
        data = data[10:]

        # Walk through the data, and map it to actual voltages
        # First invert the data (ya rly)
        data = data * -1 + 255

        # Now, we know from experimentation that the scope display range is actually
        # 30-229.  So shift by 130 - the voltage offset in counts, then scale to
        # get the actual voltage.
        voltscale = self.voltscale
        voltoffset = self.voltoffset
        data = (data - 130.0 - voltoffset / voltscale * 25) / 25 * voltscale
        return data

    def capture(self):
        """
        Capture screen full of data.
        """
        data = self.capture_voltage()

        # Create time scale
        points = len(data)
        perdiv = points / 12.0
        timescale = self.oscope.timescale
        timeoffset = self.oscope.timeoffset
        end = points / perdiv * timescale / 2.0
        begin = -end
        step = timescale / perdiv
        times= numpy.arange(begin + timeoffset, end + timeoffset, step)

        # If we generated too many points due to overflow, crop the length of time.
        if (times.size > data.size):
            times= times[:points]

        return data, times

    @property
    def rms(self):
        self.write(":MEAS:VRMS? %s" % self.id)
        return float(self.read(20))

    @property
    def freq(self):
        self.write(":MEAS:FREQ? %s" % self.id)
        return float(self.read(20).lstrip(">"))

    @property
    def zero(self):
        adjusted = self.rms / self.voltscale
        return adjusted < 0.1

    def wait_freq(self, freq, wait_time=None):
        start = time.time()
        measured = self.freq
        while abs((measured - freq) / freq) > 0.1:
            if wait_time and (time.time() - start > wait_time):
                return False
            measured = self.freq
        return True
