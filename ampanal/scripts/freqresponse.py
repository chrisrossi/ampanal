import math
from matplotlib import pyplot as plot
from matplotlib import ticker

from ..oscope import Oscope
from ..funcgen import FunctionGenerator


def main():
    worker = FreqResponse()
    try:
        worker.calibrate()
        start = 20
        end = 20000
        exp = math.sqrt(math.sqrt(2))
        freqs = list(exprange(start, end, exp))
        gains = map(worker.measure, freqs)

        fig, ax = plot.subplots()
        ax.plot(freqs, gains)
        ax.set_xscale('log', basex=2)
        ax.set_xticks(list(exprange(start, end, 2)))
        ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
        ax.set_xlim(freqs[0], freqs[-1])
        ax.set_ylim(min(-3.0, min(gains)), max(3.0, max(gains)))
        plot.show()
    finally:
        worker.oscope.local_mode()


class FreqResponse(object):

    def __init__(self):
        self.oscope = Oscope()
        self.fg = FunctionGenerator()
        self.fg.start()

    def calibrate(self, freq=1000):
        oscope = self.oscope
        channel = oscope.one
        fg = self.fg

        oscope.timescale = self.timescale_for_freq(freq)
        fg.sine(freq)
        oscope.local_mode()
        while True:
            typed = raw_input("calibrate> ")
            if typed == '':
                break

        self.zerodb = channel.rms

    def timescale_for_freq(self, freq):
        period = 1.0 / freq
        for scale in self.oscope.timescales:
            if scale * 4 > period:
                return scale

    def measure(self, freq):
        oscope = self.oscope
        channel = oscope.one
        fg = self.fg
        oscope.timescale = self.timescale_for_freq(freq)

        # Make abolutely certain were not measuring the prev freq
        #fg.silence()
        #while not channel.zero:
        #    pass

        fg.sine(freq)
        print "%0.3f hz" % freq
        measured = channel.freq
        while abs((measured - freq) / freq) > 0.1:
            measured = channel.freq

        fg.silence()
        return 20 * math.log10(channel.rms / self.zerodb)


def exprange(start, end, exp):
    n = float(start)
    while n < end:
        yield n
        n *= exp
