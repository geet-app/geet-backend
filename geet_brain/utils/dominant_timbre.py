import numpy as np
import math
from scipy.io import wavfile
from functools import reduce



def get_dominant_timbre(wav):
    amp, freq = fft_and_simplify_data(wav)
    indices = np.argsort(amp)[::-1]

    amps, freqs = [], []
    a = []
    i = 0

    for index in indices:
        apnd = True

        for e in a:
            if not np.any(abs(e - freq[index]) <= 50) and freq[index] > a[0]:
                apnd = True
            else:
                apnd = False
                break

        if apnd:
            a.append(freq[index])

            freqs.append(np.round(freq[index]))
            amps.append(np.round(amp[index]))

            i += 1
        if i == 5:
            break

    lcm = 1
    amps = np.array(amps)
    lcm = np.lcm.reduce(amps.astype(int))

    s = ""
    ar = []
    for a in amps:
        if lcm != 0:
            ar.append(a / lcm)
        else:
            ar.append(0)
    m = math.floor(np.log10(np.nanmin(ar))) if np.isnan(np.nanmin(ar)) else math.floor(np.log10(np.nanmin(ar)))

    ratio = []
    for a in ar:
        ratio.append(np.round(a * 10 ** (m * -1)))

    return amps, freqs, ratio


def fft_and_simplify_data(wav):
    rate, aud_data = wavfile.read(wav)

    len_data = len(aud_data)

    print(len_data)
    channel = np.zeros((2 ** (int(np.ceil(np.log2(len_data)))), 2))
    channel[0:len_data] = aud_data

    fourier = np.fft.fft(channel)
    # fft has a complex return value, getting abs val to make it easier
    # to compute
    amplitudes = np.absolute(fourier)

    # fft returns the amplitude of different frequencies, this here is an
    # array of different frequencies
    frequencies = np.linspace(0, rate, len(amplitudes))

    amplitudes = amplitudes[0 : len(amplitudes) // 2]
    frequencies = frequencies[0 : len(frequencies) // 2]

    return amplitudes, frequencies
