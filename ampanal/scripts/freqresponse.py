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
        worker.fg.silence()

        fig, ax = plot.subplots()
        ax.plot(freqs, gains)
        ax.set_xscale('log', basex=2)
        ax.set_xticks(list(exprange(start, end, 2)))
        ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
        ax.set_xlim(freqs[0], freqs[-1])
        limits = filter(lambda x: x is not None, gains)
        ax.set_ylim(min(-5.0, min(limits) - 2.0), max(5.0, max(limits) + 2.0))
        plot.show(block=False)
        while True:
            try:
                raw_input("measure> ")
            except EOFError:
                break
            gains = map(worker.measure, freqs)
            worker.fg.silence()
            ax.plot(freqs, gains)
            plot.show(block=False)
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
            try:
                freq = int(typed)
                oscope.timescale = self.timescale_for_freq(freq)
                fg.sine(freq)
            except:
                pass

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
        fg.sine(freq)
        if channel.wait_freq(freq, 2):
            rms = channel.rms
            if rms:
                return 20 * math.log10(rms / self.zerodb)


def exprange(start, end, exp):
    n = float(start)
    while n < end:
        yield n
        n *= exp
