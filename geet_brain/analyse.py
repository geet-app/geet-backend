from utils import download_song, dominant_timbre, tempo
from utils import non_silent

import numpy as np

from pydub import AudioSegment, silence


def f(x, w=15):
    x = np.abs(x / w)
    sqr = 1 - (x**2 / 9)
    inv = np.zeros_like(x)

    mask = x <= 2.2
    inv[mask] = np.where(x[mask] != 0, 1 / x[mask], 0)

    return np.where(mask, sqr, inv)


class Analyse:
    def __init__(self, audio, song_id, index) -> None:
        self.audio = audio
        # self.user_id = user_id
        self.song_id = song_id
        # self.index = index

        _non_silent = non_silent.get_nonsilent(
            f"./static/splitted/mdx_extra_q/{self.song_id}/vocals.mp3"
        )

        self.end_data = {
            "instrumental": f"./static/splitted/mdx_extra_q/{self.song_id}/instrumental.mp3",
            "end": _non_silent[-1][-1],
            "vocal_sections": _non_silent,
        }

        self.data = {
            "song": song_id,
            "netscore": 0,
            "vocal_sections": self.end_data["vocal_sections"],
            "length_diff": [],
            "voc_length_diff_lens": [],
            "voc_length_diff_lens_silent": [],
            "rec_length_diff_lens": [],
            "rec_length_diff_lens_silent": [],
            "breaks_diff": [],
            "signed_net_breaks_diff": 0,
            "recording_freq": [],
            "vocal_freq": [],
            "freq_diff": [],
            "recording_timbre": [],
            "vocal_timbre": [],
            "recording_tempo": [],
        }

        self.song = song_id

        self.vocals = AudioSegment.from_mp3(
            f"./static/splitted/mdx_extra_q/{self.song_id}/vocals.mp3"
        )[self.data["vocal_sections"][0][0] : self.data["vocal_sections"][0][1]]

        self.total_vocals = len(self.end_data["vocal_sections"])

        self.relative_silence_threshold = 8

        self.rec_non_silent = silence.split_on_silence(
            self.audio,
            min_silence_len=250,
            silence_thresh=self.audio.dBFS - 12,
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
            self.audio,
            min_silence_len=250,
            silence_thresh=self.audio.dBFS - 12,
            seek_step=250,
        )

        self.timbre = None
        self.v_timbre = None

    def analyse(self):
        self.netscore = 0

        self.net_length_score = 0
        self.breaks_score = 0
        self.timbre_score = 0
        self.frequency_score = 0
        self.tempo_score = 0

        self.get_length_diff()
        self.get_breaks_taken()
        self.get_timbre()
        self.get_frequency()
        self.get_tempo()

        self.netscore += 0.2 * self.tempo_score
        self.netscore += 0.15 * self.timbre_score
        self.netscore += 0.15 * self.frequency_score
        self.netscore += 0.25 * self.net_length_score
        self.netscore += 0.25 * self.breaks_score

        print("NETSCORE", self.netscore)
        return self.netscore

    def get_length_diff(self):
        self.length_diff = 0

        for i in self.rec_non_silent:
            self.length_diff += len(i)
            self.data["rec_length_diff_lens"].append(len(i))

        for i in self.rec_silent:
            self.data["rec_length_diff_lens_silent"].append(len(i))  # review

        for i in self.voc_non_silent:
            self.length_diff -= len(i)
            self.data["voc_length_diff_lens"].append(len(i))

        for i in self.voc_silent:
            self.data["voc_length_diff_lens_silent"].append(len(i))

        x = self.length_diff / (10**3)
        self.data["length_diff"] = x

        self.net_length_score += f(self.data["length_diff"], 2) / self.total_vocals

    def get_breaks_taken(self):
        self.num_of_breaks = len(self.rec_non_silent) - len(self.voc_non_silent)

        self.data["breaks_diff"] = self.num_of_breaks

        self.breaks_score += f(self.num_of_breaks, 3) / self.total_vocals

    def calculate_timbre_score(timbre, v_timbre):
        amps1, freqs1, ratio1 = timbre
        amps2, freqs2, ratio2 = v_timbre

        s = 0
        for i in enumerate(ratio1):
            a = ratio2[i] - ratio1[i]
            a = 1 if a == 0 else a

            s += f(a * (freqs2[i] - freqs1[i]), 50)

        return s / len(ratio1)

    def get_timbre(self):
        # self.initialise_frequency_data()

        self.timbre = dominant_timbre.get_dominant_timbre(
            f"./static/song/{self.song_id}.wav"
        )
        self.v_timbre = dominant_timbre.get_dominant_timbre(
            f"./static/splitted/mdx_extra_q/{self.song_id}/vocals.wav"
        )

        # print(self.timbre, self.v_timbre)

        self.data["recording_timbre"] = self.timbre
        self.data["vocal_timbre"] = self.v_timbre
        # print(type(self.data["recording_timbre"]))
        # print(len(self.data["recording_timbre"]))
        # print(type(self.timbre))
        # print("\n\n\n")
        # print(type(self.data["vocal_timbre"]))
        # print(len(self.data["vocal_timbre"]))
        # print(type(self.v_timbre))
        # self.timbre_score += (
        #     self.calculate_timbre_score(
        #         self.data["recording_timbre"], self.data["vocal_timbre"]
        #     )
        #     / self.total_vocals
        # )
        amps1, freqs1, ratio1 = self.timbre
        amps2, freqs2, ratio2 = self.v_timbre
        s = 0
        for i in range(len(ratio1)):
            a = ratio2[i] - ratio1[i]
            a = 1 if np.array_equal(a, 0) else a

            s += f(a * (freqs2[i] - freqs1[i]), 50)

        foo = s / len(ratio1)

        self.timbre_score += foo / self.total_vocals

    def initialise_frequency_data(self):
        try:
            # is needed ???
            # self.audio.set_channels(1).export(
            #     f"./hard_drive/temp/{self.song_id}.wav", format="wav"
            # )
            # self.vocals.set_channels(1).export(
            #     f"./hard_drive/temp/{self.song_id}_vocals.wav", format="wav"
            # )

            self.timbre = dominant_timbre.get_dominant_timbre(
                f"./static/song/{self.song_id}.wav"
            )
            self.v_timbre = dominant_timbre.get_dominant_timbre(
                f"./static/splitted/mdx_extra_q/{self.song_id}/vocals.wav"
            )
        except Exception as e:
            print(e)

    def get_frequency(self):
        amps, freqs, r = self.timbre
        v_amps, v_freqs, r = self.v_timbre

        freqs[0] = 10 * np.round(freqs[0] / 10)
        v_freqs[0] = 10 * np.round(v_freqs[0] / 10)

        # aplitude needed ?????
        rec_max_ampl, self.recording_freq = amps[0], freqs[0]
        voc_max_ampl, self.vocal_freq = v_amps[0], v_freqs[0]

        self.data["vocal_freq"] = self.vocal_freq
        self.data["recording_freq"] = self.recording_freq

        self.frequency_score += (
            f(abs(self.recording_freq - self.vocal_freq), 40) / self.total_vocals
        )

    def get_tempo(self):
        self.tempo = 0
        t, beat_frames = tempo.get_tempo(f"./static/song/{self.song_id}.wav")
        self.tempo = t
        self.data["recording_tempo"] = 10 * (round(t / 10))

        self.tempo_score += f(self.data["recording_tempo"] - t, 10) / self.total_vocals
