from download_song import download_yt
import asyncio
from pathlib import Path

async def download_and_split(path_id):

    mypath = Path(__file__).parent.parent / "static" / "temp_things"
    proc = await asyncio.create_subprocess_shell(
        f"yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 -o {mypath}/temp_recording_{path_id}.mp3 {path_id}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    proc = await asyncio.create_subprocess_shell(
        f"demucs {mypath}/temp_recording_{path_id}.mp3 --out {mypath.parent.parent}/temp -n mdx_extra_q --two-stems vocals --mp3 -j 6",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    print(mypath.parent.parent / "temp")
    
    proc = await asyncio.create_subprocess_shell(
         f"cp {mypath.parent.parent}/temp/mdx_extra_q/{path_id}/vocals.mp3 {mypath}/recording_{path_id}.mp3",
    )

if __name__ == "__main__":
    id = "r9ixmnuGPMk"
    asyncio.run(download_and_split(id))

