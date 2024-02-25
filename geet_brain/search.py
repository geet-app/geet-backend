from ytmusicapi import YTMusic
import asyncio
from geet_brain import download_song
import threading

BROWSER_ID = ""


# from .cacher import Cache
async def store_song(song_id: str, db, Song):
    ytmusic = YTMusic("oauth.json")
    individual_song_response = ytmusic.get_song(song_id)

    individual_song_thumbnail = individual_song_response["videoDetails"]["thumbnail"][
        "thumbnails"
    ][3]["url"]
    individual_song_title = individual_song_response["videoDetails"]["title"]
    individual_song_artist = individual_song_response["videoDetails"]["author"]

    # individual_song_file = (download_song.download_yt, song_id)
    # individual_song_file = threading.Thread(
    #     target=download_song.download_yt, args=(song_id,)
    # )

    path = await download_song.download_yt(song_id)

    db_song = Song(
        song_id=song_id,
        song_title=individual_song_title,
        song_artist=individual_song_artist,
        thumb_file=individual_song_thumbnail,
        song_file=path,
    )

    db.session.add(db_song)
    db.session.commit()


async def search_song(query: str, db, Song):

    ytmusic = YTMusic("oauth.json")
    yt_response = ytmusic.search(query, filter="songs")

    response = {"songs": []}

    for result in yt_response[:5]:
        if not db.session.query(Song).filter(Song.song_id == result["videoId"]).count():
            # asyncio.create_task(store_song(result["videoId"], db, Song))
            # threading.Thread(
            #     target=store_song, args=(result["videoId"], db, Song)
            # ).start()

            await store_song(result["videoId"], db, Song)
            response["songs"].append(
                {
                    "title": result["title"],
                    "artist": result["artists"][0]["name"],
                    "song_id": result["videoId"],
                    "thumbnail": result["thumbnails"][0]["url"],
                }
            )

        else:
            db_song = (
                db.session.query(Song).filter(Song.song_id == result["videoId"]).first()
            )

            response["songs"].append(
                {
                    "title": db_song.song_title,
                    "artist": db_song.song_artist,
                    "song_id": db_song.song_id,
                    "thumbnail": db_song.thumb_file,
                }
            )

    # for song in yt_response[:5]:
    #     if not db.session.query(Song).filter(Song.song_id == song["videoId"]).count():

    #         response["songs"].append(
    #             {
    #                 "title": song["title"],
    #                 "artist": song["artists"][0]["name"],
    #                 "song_id": song["videoId"],
    #                 "thumbnail": song["thumbnails"][0]["url"],
    #             }
    #         )

    return response
