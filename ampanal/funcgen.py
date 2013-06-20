import math
import pyaudio
import struct

from itertools import islice


def packframe(i):
    return struct.pack("<h", i)


class FunctionGenerator(object):

    def __init__(self, framerate=44100):
        self.framerate = framerate
        self.function = silence_function()
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.get_format_from_width(2),
            channels=1,
            rate=self.framerate,
            output=True,
            stream_callback=self.generate,
            frames_per_buffer=2<<12
        )

    def start(self):
       self.stream.start_stream()

    def close(self):
        self.stream.close()
        self.audio.terminate()

    def generate(self, in_data, frame_count, time_info, status):
        data = ''.join(map(packframe, islice(self.function, frame_count)))
        return data, pyaudio.paContinue

    def sine(self, freq=1000, amplitude=1.0):
        self.function = iter(sine_function(amplitude, freq, self.framerate))

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
