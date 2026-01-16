# tmdb_api/services.py
import os
import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"

def fetch_popular_movies(count=30, language="ko-KR", page=1):
    """
    TMDB 인기 영화 목록을 가져옵니다. (count: 20~40 권장)
    반환: 영화 dict 리스트 (title, overview, poster_path 등 포함)
    """
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY가 .env에 없습니다.")

    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": api_key,
        "language": language,
        "page": page,
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])

    # TMDB는 한 페이지에 보통 20개 줍니다.
    # count가 20을 초과하면 page 2도 추가로 받아서 채웁니다.
    movies = results
    while len(movies) < count:
        page += 1
        params["page"] = page
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            break
        movies.extend(results)

    return movies[:count]


def poster_url(poster_path, size="w500"):
    if not poster_path:
        return ""
    return f"https://image.tmdb.org/t/p/{size}{poster_path}"
