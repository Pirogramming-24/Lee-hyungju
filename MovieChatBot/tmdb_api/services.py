import os
import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"

def _get(params_url, params):
    r = requests.get(params_url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_popular_movies(count=30, language="ko-KR"):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY가 .env에 없습니다.")

    movies = []
    page = 1
    while len(movies) < count:
        data = _get(
            f"{TMDB_BASE_URL}/movie/popular",
            {"api_key": api_key, "language": language, "page": page},
        )
        results = data.get("results", [])
        if not results:
            break

        for m in results:
            poster_path = m.get("poster_path") or ""
            m["poster_url"] = f"{POSTER_BASE}{poster_path}" if poster_path else ""
        movies.extend(results)
        page += 1

    return movies[:count]


def fetch_movie_detail(tmdb_id, language="ko-KR"):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY가 .env에 없습니다.")

    data = _get(
        f"{TMDB_BASE_URL}/movie/{tmdb_id}",
        {"api_key": api_key, "language": language},
    )
    poster_path = data.get("poster_path") or ""
    data["poster_url"] = f"{POSTER_BASE}{poster_path}" if poster_path else ""
    return data


def fetch_movie_credits(tmdb_id):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY가 .env에 없습니다.")

    data = _get(
        f"{TMDB_BASE_URL}/movie/{tmdb_id}/credits",
        {"api_key": api_key},
    )

    director = next(
        (c.get("name") for c in data.get("crew", []) if c.get("job") == "Director"),
        None
    )

    lead_actor = next(
        (c.get("name") for c in data.get("cast", []) if c.get("order") == 0),
        None
    )

    return director, lead_actor


# TMDB 장르 이름 -> 당신 코드(choices)로 매핑
# GENRE_MAP = {
#     "Action": "ACTION",
#     "Drama": "DRAMA",
#     "Comedy": "COMEDY",
#     "Romance": "ROMANCE",
#     "Thriller": "THRILLER",
#     "Horror": "HORROR",
#     "Science Fiction": "SF",
#     "Fantasy": "FANTASY",
#     "Animation": "ANIMATION",
#     "Documentary": "DOCUMENTARY",
# }

# def map_genre(detail_json):
#     genres = detail_json.get("genres") or []
#     if not genres:
#         return None
#     # 첫 번째 장르만 저장(원하면 여러개로 바꾸면 됨)
#     name = genres[0].get("name")
#     return GENRE_MAP.get(name)


GENRE_ID_MAP = {
    28: "ACTION",
    18: "DRAMA",
    35: "COMEDY",
    10749: "ROMANCE",
    53: "THRILLER",
    27: "HORROR",
    878: "SF",
    14: "FANTASY",
    16: "ANIMATION",
    99: "DOCUMENTARY",
    # 필요하면 추가
}

def map_genre_by_id(detail_json):
    genres = detail_json.get("genres") or []
    # genres: [{"id": 28, "name": "액션"}, ...]
    for g in genres:
        gid = g.get("id")
        if gid in GENRE_ID_MAP:
            return GENRE_ID_MAP[gid]
    return None

def search_movies(query, language="ko-KR", page=1):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY가 .env에 없습니다.")

    data = _get(
        f"{TMDB_BASE_URL}/search/movie",
        {"api_key": api_key, "language": language, "query": query, "page": page},
    )
    results = data.get("results", [])

    for m in results:
        poster_path = m.get("poster_path") or ""
        m["poster_url"] = f"{POSTER_BASE}{poster_path}" if poster_path else ""

    return results
