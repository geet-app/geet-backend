from ytmusicapi import YTMusic

POP_HITS = "RDCLAK5uy_nmS3YoxSwVVQk9lEQJ0UX4ZCjXsW_psU8"
HIP_HOP_HITS = "RDCLAK5uy_kw2wIlEv9llILhO0qoMTLsBBhmjzuibAc"
INDIE_HITS = "RDCLAK5uy_kFs4DBLn3pFmAiXodtYyzaB5Xa_njue3A"
ROCK_HITS = "RDCLAK5uy_k6CicQMBYujmwL9DB5xBripE9EfgeKpHM"


class Recommendations:
    def __init__(self):
        self.ytmusic = YTMusic("oauth.json")

    def pop_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=POP_HITS)
        response = {
            "songs": [
                {
                    "title": song["title"],
                    "artist": song["artists"][0]["name"],
                    "song_id": song["videoId"],
                    "thumbnail": song["thumbnails"][0]["url"],
                }
                for song in yt_response["tracks"]
            ]
        }

        return response

    def hip_hop_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=HIP_HOP_HITS)
        response = {
            "songs": [
                {
                    "title": song["title"],
                    "artist": song["artists"][0]["name"],
                    "song_id": song["videoId"],
                    "thumbnail": song["thumbnails"][0]["url"],
                }
                for song in yt_response["tracks"]
            ]
        }

        return response

    def indie_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=INDIE_HITS)
        response = {
            "songs": [
                {
                    "title": song["title"],
                    "artist": song["artists"][0]["name"],
                    "song_id": song["videoId"],
                    "thumbnail": song["thumbnails"][0]["url"],
                }
                for song in yt_response["tracks"]
            ]
        }

        return response

    def rock_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=ROCK_HITS)
        response = {
            "songs": [
                {
                    "title": song["title"],
                    "artist": song["artists"][0]["name"],
                    "song_id": song["videoId"],
                    "thumbnail": song["thumbnails"][0]["url"],
                }
                for song in yt_response["tracks"]
            ]
        }

        return response
