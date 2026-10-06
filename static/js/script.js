if (typeof searchQuery !== "undefined" && searchQuery) {
    loadSearchResults(searchQuery);
}

function loadSearchResults(query) {
    const container = document.getElementById("search-results");

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
    .then(response => {
        if (!response.ok) {
            throw new Error("Risposta del server non valida");
        }
        return response.json();
    })
    .then(movies => {
        container.innerHTML = "";

        if (movies.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <p>Nessun film trovato per questa ricerca.</p>
                </div>`;
            return;
        }

        movies.forEach(movie => {
            if (movie.Poster && movie.Poster !== "N/A") {
                container.appendChild(createMovieCard(movie));
            }
        });
    })
    .catch(error => {
        console.error("Errore nella ricerca:", error);
        container.innerHTML = `
            <div class="text-center py-4">
                <p>Si è verificato un errore durante la ricerca. Riprova più tardi.</p>
            </div>`;
    });
}

function createMovieCard(movie) {
    const col = document.createElement("div");
    col.className = "col";

    const link = document.createElement("a");
    link.href = `/movie/${movie.imdbID}`;
    link.className = "movie-card";

    const img = document.createElement("img");
    img.src = movie.Poster;
    img.alt = movie.Title;
    img.className = "movie-poster";
    img.addEventListener("error", function () {
        col.style.display = "none";
    });

    const titleDiv = document.createElement("div");
    titleDiv.className = "movie-title";
    titleDiv.textContent = `${movie.Title} (${movie.Year})`;

    link.appendChild(img);
    link.appendChild(titleDiv);
    col.appendChild(link);

    return col;
}