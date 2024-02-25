import subprocess
import asyncio
from pathlib import Path

YTDLP_PATH = "yt-dlp"
MY_PATH = Path(__file__).parent.parent.absolute() / "static" / "song"

async def download_yt(song_id, purify=False):

    file_name = f"{song_id}.mp3"
    # print(f"{YTDLP_PATH} --extract-audio --audio-format mp3 --audio-quality 0 -o {MY_PATH}/{file_name} {song_id}")
    proc = await asyncio.create_subprocess_shell(
        f"{YTDLP_PATH} --extract-audio --audio-format mp3 --audio-quality 0 -o {MY_PATH}/{file_name} {song_id}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    # print(stdout)
    # print(stderr)
    print("downloaded")
    return str(MY_PATH/file_name)
