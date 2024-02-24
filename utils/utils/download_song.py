import subprocess


def download_yt(song_id, purify=False):
    print("Downloading Song : ", song_id, "\nTo: ./hard_drive/swap \nAs : <itself>")

    command = "yt-dlp -f 251 --id https://www.youtube.com/watch?v=" + song_id
    process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
    process.wait()

    subprocess.check_output(
        f"ffmpeg -i ./{song_id}.webm -vn ./hard_drive/swap/{song_id}.mp3".split(" ")
    )

    subprocess.check_output(f"rm ./{song_id}.webm".split(" "))

    return f"/swap/{song_id}.mp3"
