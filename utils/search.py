from ytmusicapi import YTMusic
# from .cacher import Cache

def search_song(query: str):
    ytmusic = YTMusic("oauth.json")
    yt_response = ytmusic.search(query, filter="songs")
    
    # cache = Cache()

    quality_responses = []
    
    # for song in yt_response:
        # cached = cache.lookup(song["videoId"])
        # if cached:
        #     quality_responses.append(cached)
        # else:
        #     song_info = ytmusic.get_song(song["videoId"])
        #     quality_responses.append(song_info)
        #     cache.store(song["videoId"], song_info)

    response = {
        "songs": [
            {
                "title": song["title"],
                "artist": song["artists"][0]["name"],
                "id": song["videoId"],
                "thumbnail": song["thumbnails"][0]["url"],
            }
            for song in yt_response
        ]
    }
    return response
