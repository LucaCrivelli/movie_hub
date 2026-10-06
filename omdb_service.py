import requests
import json
from requests.exceptions import RequestException
from config import OMDB_API_KEY, OMDB_BASE_URL


def _safe_get(params):
    """Esegue una richiesta GET a OMDb gestendo timeout ed errori di rete.
    Restituisce il JSON decodificato, oppure None se qualcosa va storto."""
    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()  # solleva un errore se lo status non è 200
        return response.json()
    except RequestException as e:
        print(f"Errore nella chiamata a OMDb: {e}")
        return None


def get_featured_movies():
    movies = []
    for title in FEATURED_MOVIES:
        data = _safe_get({"t": title, "apikey": OMDB_API_KEY})
        if data and data.get("Response") == "True":
            movies.append({
                "title": data.get("Title"),
                "poster": data.get("Poster"),
                "year": data.get("Year"),
                "imdb_id": data.get("imdbID")
            })
        else:
            print(f"Attenzione: film non trovato o errore -> {title}")
    return movies


def search_movies(query):
    print(f"Query ricevuta: {repr(query)}")  # DEBUG temporaneo
    if len(query) < 3:
        data = _safe_get({"t": query, "apikey": OMDB_API_KEY})
        if data and data.get("Response") == "True":
            movie = {
                "Title": data.get("Title"),
                "Year": data.get("Year"),
                "imdbID": data.get("imdbID"),
                "Poster": data.get("Poster"),
                "Type": data.get("Type")
            }
            return [movie] if movie.get("Type") != "game" else []
        return []

    data = _safe_get({"s": query, "apikey": OMDB_API_KEY})
    if data and data.get("Response") == "True":
        results = data.get("Search", [])
        return [r for r in results if r.get("Type") != "game"]
    return []

def get_movie_details(imdb_id):
    data = _safe_get({"i": imdb_id, "apikey": OMDB_API_KEY})
    if data and data.get("Response") == "True":
        return data
    return None

def get_movie_details_by_title(title):
    """Recupera i dettagli completi di un film cercando per titolo esatto (usato per il precaricamento)."""
    data = _safe_get({"t": title, "apikey": OMDB_API_KEY})
    if data and data.get("Response") == "True":
        return data
    return None

def load_featured_titles():
    """Legge la lista dei titoli in evidenza dal file JSON."""
    with open("trending_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("featured_movies", [])


FEATURED_MOVIES = load_featured_titles()