import subprocess


async def download_yt(song_id, purify=False):
    print("Downloading Song : ", song_id, "\nTo: ./static/song \nAs : <itself>")

    command = "yt-dlp -f 251 --id https://www.youtube.com/watch?v=" + song_id
    process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
    process.wait()

    subprocess.check_output(
        f"ffmpeg -i ./{song_id}.webm -vn ./static/song/{song_id}.wav".split(" ")
    )

    subprocess.check_output(f"rm ./{song_id}.webm".split(" "))

    print("Downloaded Song : ", song_id, "\nTo: ./static/song \nAs : <itself>")

    return f"./static/song/{song_id}.wav"
