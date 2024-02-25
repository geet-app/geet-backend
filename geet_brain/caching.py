import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def cache_song(song_id, song_file, thumb_file):
    pass
