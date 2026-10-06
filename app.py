from flask import Flask, render_template, request, jsonify
from models.conn import db
from config import DATABASE_URI


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

db.init_app(app)

# dopo init_app, rischio import circolari
from models.model import Movie
from omdb_service import search_movies, get_movie_details, get_movie_details_by_title, FEATURED_MOVIES
from sqlalchemy import func

FEATURED_IMDB_IDS = []  # popolata all'avvio da preload_featured_movies()


def preload_featured_movies():
    """All'avvio, salva nel DB i film in evidenza (se non già presenti) e restituisce i loro imdb_id."""
    ids = []
    for title in FEATURED_MOVIES:
        existing = db.session.execute(db.select(Movie).filter(func.lower(Movie.title) == func.lower(title))).scalars().first()

        if existing:
            ids.append(existing.imdb_id)
            continue

        data = get_movie_details_by_title(title)
        app.logger.warn(f'input title: {title} data: {data} existing: {existing}')
        if data:
            movie = Movie(
                imdb_id=data.get("imdbID"),
                title=data.get("Title"),
                poster_url=data.get("Poster"),
                rating=data.get("imdbRating"),
                release_date=data.get("Released"),
                genre=data.get("Genre"),
                plot=data.get("Plot"),
                cast=data.get("Actors")
            )
            db.session.add(movie)
            db.session.commit()
            ids.append(movie.imdb_id)
        else:
            print(f"Impossibile precaricare: {title}")

    return ids

@app.route("/")
def home():
    featured = db.session.execute(db.select(Movie).filter(Movie.imdb_id.in_(FEATURED_IMDB_IDS))).scalars().all()
    return render_template("home.html", movies=featured)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return render_template("search_results.html", query=query)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    if query:
        results = search_movies(query)
    else:
        results = []
    return jsonify(results)

@app.route("/movie/<imdb_id>")
def movie_detail(imdb_id):
    # Controlla se il film è già nel DB
    movie = db.session.execute(db.select(Movie).filter_by(imdb_id=imdb_id)).scalars().first()

    # Se non c'è, chiama OMDb e salva nel DB
    if movie is None:
        data = get_movie_details(imdb_id)

        if data is None:
            return render_template("error.html",  message="Film non trovato o servizio momentaneamente non disponibile."), 404

        movie = Movie(
            imdb_id=data.get("imdbID"),
            title=data.get("Title"),
            poster_url=data.get("Poster"),
            rating=data.get("imdbRating"),
            release_date=data.get("Released"),
            genre=data.get("Genre"),
            plot=data.get("Plot"),
            cast=data.get("Actors")
        )
        db.session.add(movie)
        db.session.commit()

    # movie esiste sempre (letto dal DB o appena salvato)
    return render_template("movie_detail.html", movie=movie)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Pagina non trovata."), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", message="Errore interno del server. Riprova più tardi."), 500
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea il file database.db e le tabelle se non esistono
        FEATURED_IMDB_IDS = preload_featured_movies()
    app.run(debug=True)