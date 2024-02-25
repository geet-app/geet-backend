import asyncio

async def convert_file(fp):
    proc = await asyncio.create_subprocess_shell(f"ffmpeg -y -i {fp} {fp.rstrip('.mp3')}.wav")
    await proc.communicate()

