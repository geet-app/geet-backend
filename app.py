from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from geet_brain.recommendations import Recommendations
from geet_brain import analyse
from geet_brain import lyrics
from geet_brain import synced_lyrics
from geet_brain import search
from geet_brain import song
from geet_brain import foobar  # temporary import
from geet_brain import download_song, gradient_colors

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# import redis
import os
from flask import Flask, render_template, request, url_for, redirect, send_file
from sqlalchemy.sql import func
from dotenv import load_dotenv

from pydub import AudioSegment

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


@app.route("/analyse/<id>/<analysis_uid>", methods=["POST"])
async def analyse_song(id, analysis_uid):

    if id is None:
        return jsonify({"error": "No song id provided"}), 400
    if analysis_uid is None:
        return jsonify({"error": "No analysis_uid provided"}), 400

    recording_audio_path = (
        Path(__file__).parent / "static" / "temp_things" / "recording_242424353.mp3"
    ).absolute()

    recording = AudioSegment.from_mp3(recording_audio_path)

    if Song.query.filter_by(song_id=id).first() is None:
        song_obj = await search.store_song(id, db, Song)
        # await synced_lyrics.separate_vocal(song_obj, db)
    else:
        song_obj = Song.query.filter_by(song_id=id).first()
        # if song_obj.vocal_file is None:
        # await synced_lyrics.separate_vocal(song_obj, db)

    song_obj.song_file = "/Users/pranjalrastogi/projects/HACKATHON2024/arnavsplayground/geet-backend/static/song/LJzp_mDxaT0.wav"
    song_obj.vocal_file = "/Users/pranjalrastogi/projects/HACKATHON2024/arnavsplayground/geet-backend/static/splitted/mdx_extra_q/LJzp_mDxaT0/vocals.wav"
    song_obj.instrumental_file = "/Users/pranjalrastogi/projects/HACKATHON2024/arnavsplayground/geet-backend/static/splitted/mdx_extra_q/LJzp_mDxaT0/instrumental.wav"

    analyser_obj = analyse.Analyser(
        recording,
        song_obj,
    )

    data = analyser_obj.analyse()

    color_scheme = gradient_colors.colorize(song_obj.thumb_file)

    data["recordingURL"] = recording_audio_path
    data["originalVocalsURL"] = f"static/splitted/mdx_extra_q/{id}/vocals.mp3"
    data["bgColor"] = color_scheme[0]

    return data

    # audio_path = "temp_things/recording.mp3"

    # recording = AudioSegment.from_mp3(audio_path)
    # audio_data, sample_rate = librosa.load(audio_path)

    # anal = Analyse(recording, "LJzp_mDxaT0")

    # print(anal.analyse())

    # audio_file = request.files["audio"]
    # audio_data = audio_file.read()

    audio_file = "temp_things/recording.mp3"
    audio_data = AudioSegment.from_file(audio_file)
    print(audio_data)
    # data = request.get_json()
    # song_id = data["song_id"]

    song_id = "LJzp_mDxaT0"

    analyser = analyse.Analyser(audio_data, song_id)

    return jsonify(analyser.analyse())


@app.route("/synced-lyrics/<id>", methods=["GET"])
async def get_synced_lyrics(id):
    if id is None:
        return jsonify({"error": "No song id provided"}), 400

    song = Song.query.filter_by(song_id=id).first()
    if song is None:
        await search.store_song(id, db, Song)
        song = Song.query.filter_by(song_id=id).first()
    if song.lyrics_synced is None:
        lyrics, times = await synced_lyrics.get_timesynced_lyrics(db, app, id, song)
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
        app.run(debug=True, host="0.0.0.0", port=5302)
