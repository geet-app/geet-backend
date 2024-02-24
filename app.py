from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import request

from geet_brain.recommendations import Recommendations
from geet_brain.analyse import Analyse
from geet_brain import lyrics
from geet_brain import search
from geet_brain import foobar  # temporary import

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

import os
from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/lyrics", methods=["POST"])
def get_lyrics():
    data = request.get_json()
    print(data)
    artist_name = data["artist_name"]
    song_name = data["song_name"]

    if data["lang"] == "en":
        return jsonify(lyrics.en_fetch_lyrics(artist_name, song_name))
    else:
        return jsonify(lyrics.hn_fetch_lyrics(artist_name, song_name))


@app.route("/recommendations/<genre>", methods=["GET"])
def get_recommendations(genre):
    recommendations = Recommendations()

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


@app.route("/search", methods=["GET"])
def search_songs():
    data = request.get_json()
    query = data["query"]

    return jsonify(search.search_song(query))


@app.route("/init/<id>", methods=["POST"])
def initialize_song(id):
    song = (
        foobar.foo()
    )  # temporary call, should be replaced by cahcing which will be done by pjr

    if not song.initialised:
        song.initialise()


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
    app.run(debug=True)
