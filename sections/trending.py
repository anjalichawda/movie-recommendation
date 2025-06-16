import streamlit as st
import requests
from sections.recommendations import is_kid_friendly

def get_trending_movies(TMDB_API_KEY, TMDB_HEADERS):
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, headers=TMDB_HEADERS)
        response.raise_for_status()
        return response.json().get('results', [])[:10]
    except:
        return []

def trending_section(movies, similarity, user_type, KIDS_KEYWORDS, EXPLICIT_KEYWORDS, TMDB_API_KEY, TMDB_HEADERS):
    st.header("🔥 Trending This Week")
    with st.spinner("Loading trending movies..."):
        # Pass TMDB_API_KEY and TMDB_HEADERS to the get_trending_movies function
        trending_movies = get_trending_movies(TMDB_API_KEY, TMDB_HEADERS)
        displayed_count = 0
        for movie in trending_movies:
            tmdb_title = movie.get('title', '')
            movie_data = movies[movies['title'].str.lower() == tmdb_title.lower()]
            if user_type == "Kids" and not movie_data.empty:
                if not is_kid_friendly(movie_data.iloc[0]['tags'], KIDS_KEYWORDS, EXPLICIT_KEYWORDS):
                    continue
            displayed_count += 1
            with st.expander(f"{tmdb_title} ({movie.get('release_date', 'N/A')})", expanded=False):
                col1, col2 = st.columns([1, 2])
                with col1:
                    poster_path = movie.get('poster_path')
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"
                    st.image(poster_url, use_container_width=True)
                with col2:
                    st.subheader(tmdb_title)
                    st.write(f"**Rating:** {movie.get('vote_average', 'N/A')}/10")
                    st.write(f"**Overview:** {movie.get('overview', 'Not available')}")
            if displayed_count >= 10:
                break
