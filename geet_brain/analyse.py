from pydub import AudioSegment
from time import time
from . import webscraper

from pydub import silence, AudioSegment
from pydub.effects import normalize
from hashlib import sha256

import numpy as np
import scipy.io.wavfile as wavfile
import librosa

import os
from subprocess import check_output, Popen
import shlex
import glob

from PIL import Image, ImageDraw, ImageFont

import lzma
import pickle
import math
import json


def f(x, w=15):
    x = abs(x / w)
    sqr = 1 - (x**2 / 9)
    inv = 0

    try:
        inv = 1 / x
    except:
        return sqr

    if x <= 2.2:
        return sqr
    else:
        return inv


class Analyse:
    # recording is the AudioSegment object
    # ID        is the ID of the song
    def __init__(self, recording, ID, index):
        self.ID = ID
        self.index = index
        with open("./hard_drive/sessions/" + ID + ".json") as f:
            self.data = json.load(f)

        self.recording = recording
        self.song = webscraper.load(self.data["song"])

        self.vocals = AudioSegment.from_mp3(
            f"./hard_drive/swap/{self.song.vocals}.mp3"
        )[self.data["vocal_sections"][index][0] : self.data["vocal_sections"][index][1]]

        self.relative_silence_threshold = 8

        self.rec_non_silent = silence.split_on_silence(
            self.recording,
            min_silence_len=250,
            silence_thresh=recording.dBFS - 12,
            seek_step=250,
        )
        self.voc_non_silent = silence.split_on_silence(
            self.vocals,
            min_silence_len=250,
            silence_thresh=self.vocals.dBFS - 12,
            seek_step=250,
        )

        self.voc_silent = silence.detect_silence(
            self.vocals,
            min_silence_len=250,
            silence_thresh=self.vocals.dBFS - 12,
            seek_step=250,
        )
        self.rec_silent = silence.detect_silence(
            self.recording,
            min_silence_len=250,
            silence_thresh=self.recording.dBFS - 12,
            seek_step=250,
        )

        # print("*" * 50)
        # print("DATA", self.data)
        # print("*" * 50)

    def commit(self):
        path = f"./hard_drive/sessions/{self.ID}.{self.index}.json"

        open(path, "x").close()
        with open(path, "w+") as f:
            json.dump(self.data, f)

    def clean(self):
        cmd = f"rm ./hard_drive/tmp/*{self.ID}*"

        arg = shlex.split(cmd)
        arg = arg[:-1] + glob.glob(arg[-1])

        p = Popen(arg)

    def analyse(self, caclulate_freq_score=True):
        self.netscore = 0

        self.get_length_diff()
        self.get_breaks_taken()
        self.get_timbre()  # already at best
        self.get_frequency()  # already at best
        self.get_tempo()  # update
        # self.get_spectral_centroid_analyser()

        """
        self.netscore += 0.2 * self.tempo_score 
        self.netscore += 0.1 * self.timbre_score 
        self.netscore += 0.1 * self.frequency_score
        self.netscore += 0.1 * self.spectral_centroid_score
        self.netscore += 0.25 * self.net_length_score 
        self.netscore += 0.25 * self.breaks_score
        """
        print("\033[91m", "NET [ ", self.netscore, "]\033[0m")
        return self.netscore

    def get_length_diff(self):
        self.length_diff = 0
        for el in self.rec_non_silent:
            self.length_diff = self.length_diff + len(el)
            self.data["rec_length_diff_lens"].append(len(el))

        for el in self.rec_silent:
            self.data["rec_length_diff_lens_silent"].append(len(el))

        for el in self.voc_non_silent:
            self.length_diff = self.length_diff - len(el)
            self.data["voc_length_diff_lens"].append(len(el))

        for el in self.voc_silent:
            self.data["voc_length_diff_lens_silent"].append(len(el))

        x = self.length_diff / (10**3)
        self.data["length_diff"] = x

        print("\033[91m", "length diff", self.length_diff, "\033[0m")

    def get_breaks_taken(self):
        self.num_of_breaks = len(self.rec_non_silent) - len(self.voc_non_silent)
        self.data["breaks_diff"] = self.num_of_breaks

        print("\033[91m", "breaks taken score", self.num_of_breaks, "\033[0m")

    def get_timbre(self):
        self.initialise_frequency_data()

        self.data["recording_timbre"] = self.timbre
        self.data["vocal_timbre"] = self.v_timbre

    # self.timbre, a 2D array, each row contains the data for timbre of
    # a given segment of the song

    def initialise_frequency_data(self, export_files=True):
        try:
            self.recording.set_channels(1).export(
                f"./hard_drive/tmp/{self.ID}.{self.index}.wav", format="wav"
            )
            self.vocals.set_channels(1).export(
                f"./hard_drive/tmp/{self.ID}.{self.index}.v.wav", format="wav"
            )
            self.timbre = get_dominant_timbre(
                f"./hard_drive/tmp/{self.ID}.{self.index}.wav"
            )
            self.v_timbre = get_dominant_timbre(
                f"./hard_drive/tmp/{self.ID}.{self.index}.v.wav"
            )
        except Exception as ex:
            print(ex)
            print("short recording ?")

    def calculate_timbre_score(timbre, v_timbre):
        amps1, freqs1, ratio1 = timbre
        amps2, freqs2, ratio2 = v_timbre

        s = 0
        for i, el in enumerate(ratio1):
            a = ratio2[i] - ratio1[i]
            a = 1 if a == 0 else a

            s += f(a * (freqs2[i] - freqs1[i]), 50)

        return s / len(ratio1)

    def get_frequency(self):
        amps, freqs, r = self.timbre
        v_amps, v_freqs, r = self.v_timbre

        freqs[0] = 10 * round(freqs[0] / 10)
        v_freqs[0] = 10 * round(v_freqs[0] / 10)

        rec_max_ampl, self.recording_freq = amps[0], freqs[0]
        voc_max_ampl, self.vocal_freq = v_amps[0], v_freqs[0]

        self.data["vocal_freq"] = self.vocal_freq
        self.data["recording_freq"] = self.recording_freq

    def get_tempo(self, export_files=True):
        self.tempo = 0
        self.tempo_score = 0

        t, beat_frames = get_tempo(f"./hard_drive/tmp/{self.ID}.{self.index}.wav")
        self.tempo = t
        self.data["recording_tempo"] = 10 * (round(t / 10))

        print("\033[91m", "tempo score :", self.tempo, "\033[0m")

    def get_spectral_centroid_analyser(self, export_files=True):
        self.centroid, self.v_centroid = [], []
        self.spectral_centroid_score = 0

        spec_centroid = get_spectral_centroid(
            f"./hard_drive/tmp/{self.ID}.{self.index}.wav"
        )
        self.centroid = spec_centroid[0]
        centroid_times = librosa.times_like(spec_centroid)

        v_spec_centroid = get_spectral_centroid(
            f"./hard_drive/tmp/{self.ID}.{self.index}.v.wav"
        )
        self.v_centroid = v_spec_centroid[0]

        self.negative_spec_centroid_diff = []
        self.positive_spec_centroid_diff = []

        scdiff = []
        for i, sc in enumerate(spec_centroid[0]):
            try:
                diff = sc - v_spec_centroid[0][i]
                scdiff.append(diff)

                if diff < 0:
                    self.negative_spec_centroid_diff.append(centroid_times[i])
                else:
                    self.positive_spec_centroid_diff.append(centroid_times[i])

            except Exception as ex:
                pass

        self.data["recording_is_brighter"] = self.positive_spec_centroid_diff
        self.data["vocals_are_brighter"] = self.negative_spec_centroid_diff
        self.data["brightness_diff"] = scdiff

    def get_color(self, netscore):
        self.color = webscraper.rgbtohex(
            (int(255 * (1 - netscore)), int(255 * netscore), 0)
        )

        return self.color

    def create_image(self):
        img = Image.new("RGB", (256, 256), color=webscraper.hextorgb(self.color))
        font = ImageFont.truetype("./static/fonts/roboto.ttf", 24)
        draw = ImageDraw.Draw(img)

        draw.text((16, 8), "I scored", font=font)

        font = ImageFont.truetype("./static/fonts/roboto.ttf", 18)
        draw.text(
            (16, 144),
            f"In the song, \n{self.song.name} \nCan you score more ?",
            font=font,
        )

        font = ImageFont.truetype("./static/fonts/roboto_bold.ttf", 72)
        draw.text(
            (48, 48),
            f"{str(int(self.netscore * 10))}/10",
            font=font,
            fill=(255, 193, 129),
        )

        font = ImageFont.truetype("./static/fonts/cursive.ttf", 16)
        draw.text((160, 224), "~ Hitokara", font=font)

        img.save(f"./static/scorecards/{self.ID}.jpg")

    """
    def get_problem_areas_between_audio_and_rec (self):
        AudioSegment.from_mp3(f'./hard_drive/swap/{self.song.ID}.mp3').export (
                f'./hard_drive/wav/{self.song.ID}.wav',format="wav"
            )
        AudioSegment.from_mp3(self.mixed_path).export(self.mixed_path+".wav",format="wav")
        self.problem_areas = self.get_problem_areas(
                self.mixed_path,
                f'./hard_drive/wav/{self.song.ID}'
            )

        try:
            check_output(f'rm ./hard_drive/wav/{self.song.vocals}.wav'.split(" "))
        except:
            pass
    def get_problem_areas(self,aud_1_fname,aud_2_fname):
        aud_1 = self.get_formatted_spectrograph(aud_1_fname)
        aud_2 = self.get_formatted_spectrograph(aud_2_fname)

        arr = []
        points = []

        print(len(aud_1),len(aud_2))

        for i in range(len(aud_1)):
            if aud_1[i] == aud_2[i]:
                arr.append(1)
            else:
                points.append(i)
                arr.append(0)

        minarr = []
        problem_areas = []

        for i in range(len(points)-1) :
            if len(minarr) == 0:
                minarr.append(i)
            elif points[i + 1] == (points[i] + 1):
                minarr.append(i)
            else :
                problem_areas.append(minarr)
                minarr = []

        return problem_areas


    def get_formatted_spectrograph(self,fname):
        sig, fs = librosa.load(f'{fname}.wav')

        S = librosa.feature.melspectrogram(y=sig, sr=fs)
        print('spectrogram len',len(S))
        arr = []
        mean = 0

        for el in S:
            arr.append(el.argmax(axis=0))
            mean += arr[-1]

        mean /= len(arr)

        for i in range(len(arr)):
            if mean < arr[i]:
                arr[i] = 1
            else:
                arr[i] = 0
        return arr
    """


def create_and_export_sound(frequency, duration=1):
    fs = 44100
    frequency = int(frequency)

    if os.path.exists(f"{frequency}.wav"):
        return

    samples = np.arange(duration * fs) / fs

    signal = np.sin(2 * np.pi * frequency * samples)

    signal *= 32000

    signal = np.int16(signal)

    wavfile.write(f"{frequency}.wav", fs, signal)
    AudioSegment.from_file(f"{frequency}.wav").export(
        f"./hard_drive/raw/{frequency}.mp3", format="mp3"
    )

    os.remove(f"{frequency}.wav")


def get_dominant_timbre(wav):
    amp, freq = fft_and_simplify_data(wav)
    indices = np.argsort(amp)[::-1]

    amps, freqs = [], []
    a = []
    i = 0

    for index in indices:
        apnd = True

        for e in a:
            if not abs(e - freq[index]) <= 50 and freq[index] > a[0]:
                apnd = True
            else:
                apnd = False
                break

        if apnd:
            a.append(freq[index])

            freqs.append(round(freq[index]))
            amps.append(round(amp[index]))

            i += 1
        if i == 5:
            break

    lcm = 1
    for i in amps:
        lcm = lcm * i // math.gcd(lcm, i)

    s = ""
    ar = []
    for a in amps:
        ar.append(a / lcm)
    m = math.floor(np.log10(np.amin(ar)))

    ratio = []
    for a in ar:
        ratio.append(round(a * 10 ** (m * -1)))

    return amps, freqs, ratio


def fft_and_simplify_data(wav):
    rate, aud_data = wavfile.read(wav)

    len_data = len(aud_data)

    print(len_data)
    channel = np.zeros(2 ** (int(np.ceil(np.log2(len_data)))))
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


def get_tempo(path):
    y, sr = librosa.load(path)

    return librosa.beat.beat_track(y=y, sr=sr)


def get_spectral_centroid(path):
    y, sr = librosa.load(path)

    return librosa.feature.spectral_centroid(y=y, sr=sr)


def get_color(netscore):
    return webscraper.rgbtohex((int(255 * (1 - netscore)), int(255 * netscore), 0))
