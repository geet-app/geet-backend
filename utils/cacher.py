from app import db, Song

class Cache:
    def __init__(self):
        self.cache = {}

    def lookup(self, key):
        return self.cache.get(key)

    def store(self, key, value):
        pass
        # db.session.add(Song(song_id=key, song_file=value["videoId"], thumb_file=value["thumbnails"][0]["url"]))
        # db.session.commit()
