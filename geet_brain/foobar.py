from .analyse import Analyse
from pydub import AudioSegment

audio_path = "temp_things/recording.mp3"

recording = AudioSegment.from_mp3(audio_path)
# audio_data, sample_rate = librosa.load(audio_path)

anal = Analyse(recording, "LJzp_mDxaT0", 0)

print(anal.analyse())

# from utils import download_song
# import asyncio


# async def fun():
#     await download_song.download_yt("LJzp_mDxaT0")


# asyncio.run(fun())
