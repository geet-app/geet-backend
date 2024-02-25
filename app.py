from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from geet_brain.recommendations import Recommendations
from geet_brain.analyse import Analyse
from geet_brain import lyrics
from geet_brain import synced_lyrics
from geet_brain import search
from geet_brain import song
from geet_brain import foobar  # temporary import
from geet_brain.utils import download_song

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# import redis
import os
from flask import Flask, render_template, request, url_for, redirect, send_file
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app)

# redis_client = redis.Redis(host="localhost", port=6379, db=0)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Song(db.Model):
    __tablename__ = "songs"
    # id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[str] = mapped_column(String, primary_key=True)
    song_artist: Mapped[str] = mapped_column(String)
    song_title: Mapped[str] = mapped_column(String)
    song_file: Mapped[str] = mapped_column(String)
    thumb_file: Mapped[str] = mapped_column(String)

    # lyrics
    vocal_file: Mapped[str] = mapped_column(String, nullable=True)
    instrumental_file: Mapped[str] = mapped_column(String, nullable=True)
    lyrics_synced: Mapped[str] = mapped_column(String, nullable=True)
    lyrics_synced_times: Mapped[str] = mapped_column(String, nullable=True)


class UserHistory(db.Model):
    __tablename__ = "user_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    song_id: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer)


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/recommendations/<genre>", methods=["GET"])
async def get_recommendations(genre):
    recommendations = Recommendations(db, Song)

    if genre == "pop":
        return jsonify(await recommendations.pop_hits())
    elif genre == "hip_hop":
        return jsonify(await recommendations.hip_hop_hits())
    elif genre == "indie":
        return jsonify(await recommendations.indie_hits())
    elif genre == "rock":
        return jsonify(await recommendations.rock_hits())
    else:
        return jsonify({"Error": "Invalid genre"})


@app.route("/search/<query>", methods=["GET"])
async def search_songs(query):
    if query is None:
        return jsonify({"error": "No query provided"}), 400
    resp = await search.search_song(query, db, Song)
    return jsonify(resp)


@app.route("/init/<id>", methods=["POST"])
def initialize_song(id):
    song = (
        foobar.foo()
    )  # temporary call, should be replaced by cahcing which will be done by pjr

    if not song.initialised:
        song.initialise()


@app.route("/song/<id>", methods=["GET"])
def get_song(id):
    if id is None:
        return jsonify({"error": "No song id provided"}), 400

    return jsonify(song.get_song(id, app, Song))


@app.route("/lyric/<id>", methods=["GET"])
def get_lyric(id):
    if id is None:
        return jsonify({"error": "No song id provided"}), 400

    return jsonify(song.get_lyric(id, app, Song))


@app.route("/lyric-artist/<artist>/<title>", methods=["GET"])
def get_lyric_2(artist, title):
    # artist = request.args.get("artist")
    # title = request.args.get("title")
    return {"lyrics": lyrics.en_fetch_lyrics(artist, title)}


@app.route("/static/song/<id>", methods=["GET"])
async def get_file(id):
    if id is None:
        return jsonify({"error": "No song id provided"}), 400

    if os.path.exists(f"static/song/{id}.mp3"):
        return send_file(
            f"static/song/{id}.mp3", as_attachment=True, mimetype="audio/mp3"
        )
    else:
        await download_song.download_yt(id)
        return send_file(
            f"static/song/{id}.mp3", as_attachment=True, mimetype="audio/mp3"
        )


@app.route("/analyse", methods=["POST"])
def analyse_song():
    audio_file = request.files["audio"]
    audio_data = audio_file.read()

    data = request.get_json()
    user_id = data["user_id"]
    song_id = data["song_id"]

    analyse = Analyse(audio_data, user_id, song_id)

    return jsonify(analyse.analyse())


@app.route("/synced-lyrics/<id>", methods=["GET"])
async def get_synced_lyrics(id):
    if id is None:
        return jsonify({"error": "No song id provided"}), 400

    song = Song.query.filter_by(song_id=id).first()
    if song is None:
        await search.store_song(id, db, Song)
        song = Song.query.filter_by(song_id=id).first()
    if song.lyrics_synced is None:
        lyrics, times = synced_lyrics.get_timesynced_lyrics(db, app, id, song)
    else:
        lyrics = song.lyrics_synced
        times = song.lyrics_synced_times
        times = times.split(",")

    return {"lyrics": lyrics, "times": times}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("*" * 50)
        print("Database created")
        print("*" * 50)
        app.run(debug=True)
