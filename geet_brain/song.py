from geet_brain import gradient_colors
from geet_brain import lyrics

def get_song(id, app, Song):
    with app.app_context():
        song = Song.query.filter_by(song_id=id).first()

    response = {
        "title": song.song_title,
        "artist": song.song_artist,
        "id": song.song_id,
        "audio": song.song_file,
        "thumbnail": song.thumb_file,
    }
    return response


def get_lyric(id, app, Song):
    with app.app_context():
        song = Song.query.filter_by(song_id=id).first()
    
    color_scheme = gradient_colors.colorize(song.thumb_file)

    _lyrics = lyrics.en_fetch_lyrics(song.song_artist, song.song_title)
    lyrics = {
        "lyrics": _lyrics,
        "bgColor": color_scheme[0],
    }

    return lyrics


# def get_lyrics():
#     data = request.get_json()
#     # print(data)
#     artist_name = data["artist_name"]
#     song_name = data["song_name"]

#     if data["lang"] == "en":
#         return jsonify(lyrics.en_fetch_lyrics(artist_name, song_name))
#     else:
#         return jsonify(lyrics.hn_fetch_lyrics(artist_name, song_name))
