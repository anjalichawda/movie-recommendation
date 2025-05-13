import pickle
import streamlit as st
import os
import requests
from PIL import Image
from datetime import datetime
from fuzzywuzzy import fuzz

# Review storage (simulating localStorage with session_state)
if 'review_count' not in st.session_state:
    st.session_state.review_count = 0
if 'reviews' not in st.session_state:
    st.session_state.reviews = {}

EXPLICIT_KEYWORDS = [
    'sex', 'adult', 'erotic', 'nude', 'violence', 'horror', 'slasher',
    'terror', 'gore', 'murder', 'drug', 'cocaine', 'heroin', 'porn',
    'rape', 'assault', 'explicit', '18+', 'xxx', 'battle', 'war'
]

KIDS_KEYWORDS = [
    'animation', 'famili', 'fantasi', 'children', 'kid', 'cartoon',
    'disney', 'pixar', 'dreamworks', 'g-rated', 'pg-rated', 'toy',
    'princess', 'fairy', 'magic', 'adventure', 'animal', 'dinosaur'
]

def is_kid_friendly(tags):
    if not isinstance(tags, str):
        return False
    tags_lower = tags.lower()
    return (any(keyword in tags_lower for keyword in KIDS_KEYWORDS) and
            not any(explicit in tags_lower for explicit in EXPLICIT_KEYWORDS))

TMDB_API_KEY = "a473dd8a2855c7017600f52110831b44"  
TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNDczZGQ4YTI4NTVjNzAxNzYwMGY1MjExMDgzMWI0NCIsIm5iZiI6MTc0NjY1MDgzMC4zOSwic3ViIjoiNjgxYmM2Y2U3ZjI0YWRjNTk4M2VjNGUxIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.oo9QsgwivgWS4lx5R2tyCg0DNRkkE5FfqTdYujfRqYE"

TMDB_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"
}

@st.cache_data
def load_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        movies = pickle.load(open(os.path.join(data_dir, "movie_list.pkl"), "rb"))
        similarity = pickle.load(open(os.path.join(data_dir, "similarity.pkl"), "rb"))
        return movies, similarity
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        st.stop()

movies, similarity = load_data()

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        response = requests.get(url, headers=TMDB_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    except:
        return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        response = requests.get(url, headers=TMDB_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

def get_trending_movies():
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, headers=TMDB_HEADERS)
        response.raise_for_status()
        return response.json().get('results', [])[:10]
    except:
        return []

def display_movie_card(movie):
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            try:
                poster = fetch_poster(movie['movie_id'])
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/500x750?text=Poster+Not+Available")
            except Exception as e:
                st.image("https://via.placeholder.com/500x750?text=Poster+Not+Available")
                st.error(f"Error loading poster: {str(e)}")
        
        with col2:
            st.subheader(movie['title'])
            details = fetch_movie_details(movie['movie_id'])
            if details:
                st.caption(f"{details.get('runtime', 'N/A')} min | {', '.join([g['name'] for g in details.get('genres', [])])} | ★ {details.get('vote_average', 'N/A')}")
                st.write(details.get('overview', 'No description available'))

            # Review box
            # Review box
            review_key = f"review_{movie['title']}"
            submit_key = f"btn_{movie['title']}"
            expander_key = f"expander_{movie['title']}"
            if expander_key not in st.session_state:
                st.session_state[expander_key] = True  # Default to open

            # Use session_state to persist the review text
            if review_key not in st.session_state:
                st.session_state[review_key] = ""

            review_text = st.text_input(
                f"Leave a review for **{movie['title']}**:",
                key=review_key
            )

            def submit_review():
                if st.session_state[review_key]:
                    st.session_state.reviews[movie['title']] = st.session_state[review_key]
                    st.session_state.review_count = len(st.session_state.reviews)
                    st.session_state[expander_key] = True  # Keep expander open
                    st.success("Thanks for your review!")

            st.button(
                f"Submit Review - {movie['title']}",
                key=submit_key,
                on_click=submit_review
            )

def trending_section():
    st.header("🔥 Trending This Week")
    with st.spinner("Loading trending movies..."):
        trending_movies = get_trending_movies()
        displayed_count = 0
        for movie in trending_movies:
            tmdb_title = movie.get('title', '')
            movie_data = movies[movies['title'].str.lower() == tmdb_title.lower()]
            if st.session_state.user_type == "Kids" and not movie_data.empty:
                if not is_kid_friendly(movie_data.iloc[0]['tags']):
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

def recommendations_section():
    st.header("🎬 Personalized Recommendations")
    available_movies = movies[movies['tags'].apply(is_kid_friendly)] if st.session_state.user_type == "Kids" else movies
    if available_movies.empty:
        st.warning("No movies available for this category")
        return

    # Use session_state to persist selected movie and show_recommendations flag
    if "selected_movie" not in st.session_state:
        st.session_state.selected_movie = available_movies['title'].values[0]
    if "show_recommendations" not in st.session_state:
        st.session_state.show_recommendations = False

    selected_movie = st.selectbox(
        "Select a movie you like",
        available_movies['title'].values,
        key="movie_selector",
        index=list(available_movies['title'].values).index(st.session_state.selected_movie)
    )

    # Update session_state when selection changes
    if selected_movie != st.session_state.selected_movie:
        st.session_state.selected_movie = selected_movie
        st.session_state.show_recommendations = False

    if st.button("Get Recommendations"):
        st.session_state.show_recommendations = True

    if st.session_state.show_recommendations:
        movie_data = movies[movies['title'] == st.session_state.selected_movie]
        if movie_data.empty:
            st.error("Movie not found")
            return
        index = movie_data.index[0]
        distances = sorted(enumerate(similarity[index]), key=lambda x: x[1], reverse=True)[1:11]
        recommended_movies = []
        for idx, _ in distances:
            movie = movies.iloc[idx]
            if st.session_state.user_type == "Kids" and not is_kid_friendly(movie['tags']):
                continue
            recommended_movies.append(movie)
            if len(recommended_movies) >= 5:
                break
        st.subheader("Recommended For You")
        for movie in recommended_movies:
            display_movie_card(movie)

def offers_section():
    st.header("🎁 Special Offers")
    st.info(f"You have submitted {st.session_state.review_count} review(s).")
    if st.session_state.review_count >= 10:
        st.success("🎉 Congratulations! Here's your BookMyShow coupon: **CINE10-OFF**")
        st.markdown("Use it to get **10% OFF** on your next movie rental!")
    else:
        st.warning("Submit 10 reviews to unlock your discount!")

def main():
    st.markdown("""<style>
        .sidebar .sidebar-content { background-color: #0e1117; }
        .stButton button { width: 100%; }
        .stExpander { margin-bottom: 1rem; border-radius: 10px; border: 1px solid rgba(250, 250, 250, 0.2); }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("🎬 PixiePicks A.I.")
        page = st.radio("Menu", ["Recommendations", "Trending", "Offers"])
        st.markdown("---")
        # Show only the current user type
        st.write(f"👤 Profile: **{st.session_state.user_type or 'Guest'}**")
        # Removed the logout button

    if page == "Recommendations":
        recommendations_section()
    elif page == "Trending":
        trending_section()
    elif page == "Offers":
        offers_section()

# Login gate
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

if not st.session_state.logged_in:
    st.error("Please log in first")
else:
    if not st.session_state.user_type:
        st.markdown("""
        <style>
/* Base style for both profile buttons */
.stButton > button {
    border: none;
    border-radius: 20px;
    padding: 1.2em 0;
    font-size: 1.2em;
    font-weight: bold;
    width: 100%;
    margin-bottom: 1.2em;
    background: #f8f9fa;
    color: #333;
    transition: all 0.3s ease-in-out;
    cursor: pointer;
    letter-spacing: 0.6px;
    position: relative;
    overflow: hidden;
    z-index: 1;
}

/* Kids button: pastel pink to lavender gradient */
div[data-testid="column"]:first-child .stButton > button {
    background: linear-gradient(135deg, #ffb6c1, #dda0dd);
    color: #fff;
    box-shadow: 0 0 18px #fbc2ebaa;
}

/* Adults button: peach to coral pink gradient */
div[data-testid="column"]:nth-child(2) .stButton > button {
    background: linear-gradient(135deg, #ffecd2, #fcb69f);
    color: #5c3d2e;
    box-shadow: 0 0 18px #fcb69faa;
}

/* Hover effects with glow */
div[data-testid="column"]:first-child .stButton > button:hover {
    transform: scale(1.07) translateY(-4px);
    box-shadow: 
        0 0 40px 12px rgba(255, 182, 193, 0.8), 
        0 8px 24px rgba(0, 0, 0, 0.15);
    filter: brightness(1.2);
    z-index: 2;
    /* Profile icon hover effect */
}
div[data-testid="column"]:first-child .stButton > button:hover::before {
    content: "🧒";
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%) scale(1.3);
    font-size: 2em;
    filter: drop-shadow(0 0 8px #ffb6c1cc);
    transition: all 0.3s;
    pointer-events: none;
}

/* Adults hover effect */
div[data-testid="column"]:nth-child(2) .stButton > button:hover {
    transform: scale(1.07) translateY(-4px);
    box-shadow: 
        0 0 40px 12px rgba(252, 182, 159, 0.8), 
        0 8px 24px rgba(0, 0, 0, 0.15);
    filter: brightness(1.2);
    z-index: 2;
}
div[data-testid="column"]:nth-child(2) .stButton > button:hover::before {
    content: "🧑";
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%) scale(1.3);
    font-size: 2em;
    filter: drop-shadow(0 0 8px #fcb69fcc);
    transition: all 0.3s;
    pointer-events: none;
}
</style>


        """, unsafe_allow_html=True)
        st.title("PixiePicks:Movie Recommendations and Reviews Platform 🎬🍿🥤")
        st.title("Who's watching?")
        cols = st.columns(2)
        with cols[0]:
            if st.button("🧒 Kids", key="kids_btn", use_container_width=True):
                st.session_state.user_type = "Kids"
                st.rerun()
        with cols[1]:
            if st.button("🧑 Adults", key="adults_btn", use_container_width=True):
                st.session_state.user_type = "Adults"
                st.rerun()
        st.stop()
    main()
