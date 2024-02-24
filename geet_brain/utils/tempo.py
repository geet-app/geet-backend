import librosa


def get_tempo(path):
    y, sr = librosa.load(path)

    return librosa.beat.beat_track(y=y, sr=sr)
