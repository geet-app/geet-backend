from bs4 import BeautifulSoup as bs
import requests
import re


def en_fetch_lyrics(artist_name, song_name):
    try:
        song_name = re.sub(r"[\W_]+", "", song_name).lower()
        artist_name = re.sub(r"[\W_]+", "", artist_name).lower()
        url = f"https://www.azlyrics.com/lyrics/{artist_name}/{song_name}.html"
        res = requests.get(url)
        soup = bs(requests.get(url).content, "html.parser")
        lyrics_div = soup.select_one(".ringtone ~ div")

        if lyrics_div:
            lyrics = lyrics_div.get_text(strip=True, separator="\n")
            return lyrics
        else:
            return {"Error": "Lyrics not found"}

    except Exception as e:
        print(e)
        return {"Error": str(e)}


def hn_fetch_lyrics(artist_name, song_name):
    try:
        param = song_name + " " + artist_name
        param = param.replace(" ", "+")
        res = requests.get(
            f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&includeMetaTags=1&query={param}"
        ).json()
        try:
            song_id = res["songs"]["data"][0]["id"]
            res = requests.get(
                f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id={song_id}"
            ).json()
            lyrics = res["lyrics"].replace("<br>", "\n")
            return {"lyrics": lyrics}
        except:
            return {"Error": "Not found"}
    except Exception as e:
        return {"Error": str(e)}
