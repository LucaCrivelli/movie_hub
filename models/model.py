from models.conn import db

class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(db.String(20), unique=True, nullable=False)  # es. "tt0816692"
    title = db.Column(db.String(200), nullable=False)
    poster_url = db.Column(db.String(300))
    rating = db.Column(db.String(10))
    release_date = db.Column(db.String(20))
    genre = db.Column(db.String(150))
    plot = db.Column(db.Text)
    cast = db.Column(db.String(300))

    def __repr__(self):
        return f"<Movie {self.title}>"