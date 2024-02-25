from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from geet_brain.recommendations import Recommendations
from geet_brain.analyse import Analyse
from geet_brain import lyrics
from geet_brain import search
from geet_brain import song
from geet_brain import foobar  # temporary import
from geet_brain.utils import download_song

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
import os
from flask import Flask, render_template, request, url_for, redirect, send_file
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app)

redis_client = redis.Redis(host="localhost", port=6379, db=0)

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
def get_recommendations(genre):
    recommendations = Recommendations(db, Song)

    if genre == "pop":
        return jsonify(recommendations.pop_hits())
    elif genre == "hip_hop":
        return jsonify(recommendations.hip_hop_hits())
    elif genre == "indie":
        return jsonify(recommendations.indie_hits())
    elif genre == "rock":
        return jsonify(recommendations.rock_hits())
    else:
        return jsonify({"Error": "Invalid genre"})


@app.route("/search/<query>", methods=["GET"])
def search_songs(query):
    if query is None:
        return jsonify({"error": "No query provided"}), 400

    return jsonify(search.search_song(query, db, Song))


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

    return jsonify(song.get_song(id, db, Song))


@app.route("/lyric/<id>", methods=["GET"])
def get_lyric(id):
    if id is None:
        return jsonify({"error": "No song id provided"}), 400

    return jsonify(song.get_lyric(id, db, Song))


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("*" * 50)
        print("Database created")
        print("*" * 50)
        app.run(debug=True)
