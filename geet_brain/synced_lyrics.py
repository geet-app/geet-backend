import asyncio
import subprocess
import whisper
import math
import requests
# from app import Song
from pathlib import Path

from geet_brain import song

YTDLP_PATH = "yt-dlp"  # the command can be global too!

MY_PATH = Path(__file__).parent.absolute() / "static"


def jaccard_similarity(sent1, sent2):
    """Find text similarity using jaccard similarity"""
    # Tokenize sentences
    token1 = set(sent1.split())
    token2 = set(sent2.split())

    # intersection between tokens of two sentences
    intersection_tokens = token1.intersection(token2)

    # Union between tokens of two sentences
    union_tokens = token1.union(token2)

    sim_ = float(len(intersection_tokens) / len(union_tokens))
    return sim_


def get_segments(vocal_filename, model_size="medium"):
    model = whisper.load_model(model_size)
    result = model.transcribe(vocal_filename)
    print(f"Segments: {len(result['segments'])}")
    return result["segments"]


def sync_segments(lyrics, segments):
    lyrics_synced = []
    lyrics_unsynced = lyrics.split("\n")

    for segment in segments:
        top_similarity = 0.0
        top_similarity_final_index = 1

        for i in range(1, len(lyrics_unsynced)):
            trial_text = " ".join(lyrics_unsynced[:i])
            trial_similarity = jaccard_similarity(trial_text, segment["text"])
            if trial_similarity > top_similarity:
                top_similarity = trial_similarity
                top_similarity_final_index = i
        lyrics_synced = lyrics_synced + list(
            map(
                lambda x: f"[{math.floor(segment['start']/60):02d}:{math.floor(segment['start'] % 60):02d}] {x}\n",
                lyrics_unsynced[:top_similarity_final_index],
            )
        )
        lyrics_unsynced = lyrics_unsynced[top_similarity_final_index:]

    lyrics_synced = lyrics_synced + list(
        map(
            lambda x: f"[{math.floor(segments[-1]['start']/60):02d}:{math.floor(segments[-1]['start'] % 60):02d}] {x}\n",
            lyrics_unsynced[0:],
        )
    )

    return lyrics_synced


def convert_to_format(lyrics_synced):
    texts = []
    times = []
    for lyric in lyrics_synced:
        spl = lyric.split()
        time = spl[0].lstrip("[").rstrip("]")
        text = " ".join(spl[1:])
        time_in_seconds = int(time.split(":")[0]) * 60 + int(time.split(":")[1])
        texts.append(text)
        times.append(time_in_seconds)

    return texts, times


async def separate_vocal(song_obj, db):

    if song_obj.instrumental_file and song_obj.vocal_file:
        return # already separated
    
    out_path = Path(song_obj.song_file).parent.parent / "splitted"

    proc = await asyncio.create_subprocess_shell(
        f"demucs {song_obj.song_file} --out {out_path} -n mdx_extra_q --two-stems vocals --mp3 -j 8",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    print(stdout, stderr)

    song_obj.instrumental_file = str((out_path / "mdx_extra_q" / song_obj.song_id / "no_vocals.mp3").absolute())
    song_obj.vocal_file = str((out_path / "mdx_extra_q" / song_obj.song_id / "vocals.mp3").absolute())
    db.session.commit()


def get_lyrics(id, app, sng):
    with app.app_context():
        lyrics = song.get_lyric(id, app, sng)
        return lyrics["lyrics"]


async def get_timesynced_lyrics(db, app, songid, song_obj):

    if song_obj.lyrics_synced:
        return song_obj.lyrics_synced, song_obj.lyrics_synced_times

    # file_name = download_song(db, id, song_obj.song_title, song_obj.song_artist, song_obj.thumb_file)
    await separate_vocal(song_obj, db)

    lyrics = get_lyrics(songid, app, song_obj)

    vocal_path = MY_PATH / "splitted" / "mdx_extra_q" / songid / "vocals.mp3"
    vocal_filename = str(vocal_path)
    segments = get_segments(vocal_filename)
    lyrics_synced = sync_segments(lyrics, segments)

    texts, times = convert_to_format(lyrics_synced)

    song_obj.lyrics_synced = "\n".join(texts)
    song_obj.lyrics_synced_times = str(times).lstrip("[").rstrip("]")
    db.session.commit()

    return texts, times
