from ytmusicapi import YTMusic


def search_song(query: str):
    ytmusic = YTMusic("oauth.json")
    yt_response = ytmusic.search(query, filter="songs")

    response = {
        "songs": [
            {
                "title": song["title"],
                "artist": song["artists"][0]["name"],
                "song_id": song["videoId"],
                "thumbnail": song["thumbnails"][0]["url"],
            }
            for song in yt_response
        ]
    }
    return response
