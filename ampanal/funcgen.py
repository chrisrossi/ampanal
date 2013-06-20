import alsaaudio as alsa
import math
import struct
import threading

from itertools import islice


def packframe(i):
    return struct.pack("<h", i)


class FunctionGenerator(threading.Thread):
    daemon = True
    stopped = False

    def __init__(self, framerate=44100, bufsize=4096):
        super(FunctionGenerator, self).__init__()
        self.framerate = framerate
        self.bufsize = bufsize
        self.function = silence_function()
        self.stream = pcm = alsa.PCM()
        pcm.setchannels(1)
        pcm.setrate(framerate)
        pcm.setformat(alsa.PCM_FORMAT_S16_LE)
        pcm.setperiodsize(bufsize)

    def close(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            frames = map(packframe, islice(self.function, self.bufsize))
            self.stream.write(''.join(frames))

    def sine(self, freq=1000, amplitude=1.0):
        self.function = sine_function(amplitude, freq, self.framerate)

    def silence(self):
        self.function = silence_function()


def sine_function(amplitude, freq, framerate):
    w = freq * math.pi * 2.0
    t = 0.0
    step = 1.0 / framerate
    amplitude *= 0x7fff
    while True:
        yield int(amplitude * math.sin(w * t))
        t += step


def silence_function():
    while True:
        yield 0.0
