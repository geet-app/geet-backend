from pydub import AudioSegment, silence


def get_song(song_id: str):
    vocal = AudioSegment.from_mp3(f"./hard_drive/swap/{song_id}.mp3")

    print(vocal[:])


get_song("bR5l0hJDnX8")


def foo():
    obj = {"a": 1, "b": 2, "c": 3}

    return ob
