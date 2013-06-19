from ..oscope import Oscope
import matplotlib.pyplot as plot


def main():
    oscope = Oscope()
    try:
        voltage, time = oscope.one.capture()

        # See if we should use a different time axis
        timescale = oscope.timescale
        if (timescale * 6 < 1e-3):
            time = time * 1e6
            tUnit = "uS"
        elif (timescale * 6 < 1):
            time = time * 1e3
            tUnit = "mS"
        else:
            tUnit = "S"

        # Plot the data
        plot.plot(time, voltage)
        plot.title("Oscilloscope Channel 1")
        plot.ylabel("Voltage (V)")
        plot.xlabel("Time (" + tUnit + ")")
        plot.xlim(time[0], time[-1])
        plot.show()
    finally:
        oscope.local_mode()
