from geet_brain.utils import download_song, dominant_timbre, tempo
from geet_brain import foobar

from pydub import AudioSegment, silence


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
    def __init__(self, audio, user_id, song_id, index) -> None:
        self.audio = audio
        self.user_id = user_id
        self.song_id = song_id
        self.index = index

        self.data  # todo
        self.song = (
            foobar.foo()
        )  # temperarory call, should be replaced by caching which will be done by pjr

        self.vocals = AudioSegment.from_mp3(
            f"./hard_drive/swap/{self.song.vocals}.mp3"
        )[self.data["vocal_sections"][index][0] : self.data["vocal_sections"][index][1]]

        self.relative_silence_threshold = 8

        self.rec_non_silent = silence.split_on_silence(
            self.recording,
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
            self.recording,
            min_silence_len=250,
            silence_thresh=self.recording.dBFS - 12,
            seek_step=250,
        )

    def analyse(self):
        self.netscore = 0

        self.get_length_diff()
        self.get_breaks_taken()
        self.get_timbre()
        self.get_frequency()
        self.get_tempo()

        self.netscore += 0.2 * self.tempo_score
        self.netscore += 0.1 * self.timbre_score
        self.netscore += 0.1 * self.frequency_score
        self.netscore += 0.1 * self.spectral_centroid_score
        self.netscore += 0.25 * self.net_length_score
        self.netscore += 0.25 * self.breaks_score

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

    def get_breaks_taken(self):
        self.num_of_breaks = len(self.rec_non_silent) - len(self.voc_non_silent)

        self.data["breaks_diff"] = self.num_of_breaks

    def get_timbre(self):
        self.initialise_frequency_data()

        self.data["recording_timbre"] = self.timbre
        self.data["vocal_timbre"] = self.v_timbre

    def initialise_frequency_data(self):
        try:
            self.audio.set_channels(1).export(
                f"./hard_drive/temp/{self.song_id}.wav", format="wav"
            )
            self.vocals.set_channels(1).export(
                f"./hard_drive/temp/{self.song_id}_vocals.wav", format="wav"
            )
            self.timbre = dominant_timbre.get_dominant_timbre(
                f"./hard_drive/tmp/{self.ID}.{self.index}.wav"
            )
            self.v_timbre = dominant_timbre.get_dominant_timbre(
                f"./hard_drive/tmp/{self.ID}.{self.index}.v.wav"
            )
        except Exception as e:
            print(e)

    def get_frequency(self):
        amps, freqs, r = self.timbre
        v_amps, v_freqs, r = self.v_timbre

        freqs[0] = 10 * round(freqs[0] / 10)
        v_freqs[0] = 10 * round(v_freqs[0] / 10)

        rec_max_ampl, self.recording_freq = amps[0], freqs[0]
        voc_max_ampl, self.vocal_freq = v_amps[0], v_freqs[0]

        self.data["vocal_freq"] = self.vocal_freq
        self.data["recording_freq"] = self.recording_freq

    def get_tempo(self):
        self.tempo = 0

        self.tempo_score = 0

        t, beat_frames = tempo.get_tempo(f"./hard_drive/tmp/{self.ID}.{self.index}.wav")
        self.tempo = t
        self.data["recording_tempo"] = 10 * (round(t / 10))
