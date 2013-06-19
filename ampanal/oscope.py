from .usbtmc import USBTMC

import numpy


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

    @property
    def timescale(self):
        """
        Voltage scale.
        """
        self.write(":TIM:SCAL?")
        return float(self.read(20))

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

    def capture(self):
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

        # For some reason 0 on the time scale is at 6/10 divisions.
        points = len(data)
        perdiv = points / 12.0
        timescale = self.oscope.timescale
        timeoffset = self.oscope.timeoffset
        print "huh?", timescale, timeoffset
        end = points / perdiv * timescale / 2.0
        begin = -end
        step = timescale / perdiv
        time = numpy.arange(begin + timeoffset, end + timeoffset, step)

        # If we generated too many points due to overflow, crop the length of time.
        if (time.size > data.size):
            time = time[:points]

        return data, time
