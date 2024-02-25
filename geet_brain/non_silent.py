from pydub import AudioSegment, silence


def get_nonsilent(path):
    audio = AudioSegment.from_mp3(path)

    arr = silence.detect_nonsilent(
        audio, min_silence_len=1000, silence_thresh=audio.dBFS - 12, seek_step=1000
    )

    ret = []
    for e in arr:
        if (e[1] - e[0]) > 5000:
            ret.append(e)

    last_couple = ret[-1]
    if (last_couple[1] - last_couple[0]) < 25000:
        ret = ret[:-1]
    else:
        last_couple = [last_couple[0], (last_couple[1] - 25000)]
        ret[-1] = last_couple

    fin = []
    for r in ret:
        if r[0] != r[1]:
            fin.append(r)

    print("removed", len(arr) - len(fin), "ammount of boilerplate")

    return fin
