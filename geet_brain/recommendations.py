from ytmusicapi import YTMusic
from geet_brain.search import store_song
from geet_brain.utils import gradient_colors

POP_HITS = "PLl5_Ali2qKoaRsOnC0j4bqAYVMD5W26PA"
HIP_HOP_HITS = "PLl5_Ali2qKoatbKApLFNY4vySMxbIZgMJ"
INDIE_HITS = "RDCLAK5uy_kFs4DBLn3pFmAiXodtYyzaB5Xa_njue3A"
ROCK_HITS = "VLPLl5_Ali2qKoZxKDeDhJ7Bt5chQdOkWv-A"


class Recommendations:
    def __init__(self, db, Song):
        self.ytmusic = YTMusic("oauth.json")
        self.db = db 
        self.Song = Song

    async def generate_response(self, yt_response):
        # response = {
        #     "songs": [
        #         {
        #             "title": song["title"],
        #             "artist": song["artists"][0]["name"],
        #             "song_id": song["videoId"],
        #             "thumbnail": song["thumbnails"][0]["url"],
        #         }
        #         for song in yt_response["tracks"]
        #     ]
        # }

        response = {"songs": []}
        for song in yt_response["tracks"][:5]:
            if (
                not self.db.session.query(self.Song)
                .filter(self.Song.song_id == song["videoId"])
                .count()
            ):
                await store_song(song["videoId"], self.db, self.Song)

            db_song = (
                self.db.session.query(self.Song)
                .filter(self.Song.song_id == song["videoId"])
                .first()
            )

            response["songs"].append(
                {
                    "title": db_song.song_title,
                    "artist": db_song.song_artist,
                    "song_id": db_song.song_id,
                    "thumbnail": db_song.thumb_file,
                    "bgColor": gradient_colors.colorize(db_song.thumb_file)[0],
                }
            )

        return response

    async def pop_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=POP_HITS)
        response = await self.generate_response(yt_response)
        return response

    async def hip_hop_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=HIP_HOP_HITS)
        response = await self.generate_response(yt_response)

        return response

    async def indie_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=INDIE_HITS)
        response = await self.generate_response(yt_response)
        return response

    async def rock_hits(self):
        yt_response = self.ytmusic.get_playlist(playlistId=ROCK_HITS)
        response = await self.generate_response(yt_response)
        return response

    def search_song(self, id):
        pass
