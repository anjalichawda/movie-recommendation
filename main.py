import streamlit as st
import pickle
import os
from sections.recommendations import recommendations_section, is_kid_friendly  # Import is_kid_friendly
from sections.trending import trending_section
from sections.offers import offers_section

# Import CSS from the 'css' folder
with open("css/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

#  TMDB API key and headers here 
TMDB_API_KEY = "a473dd8a2855c7017600f52110831b44"
TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNDczZGQ4YTI4NTVjNzAxNzYwMGY1MjExMDgzMWI0NCIsIm5iZiI6MTc0NjY1MDgzMC4zOSwic3ViIjoiNjgxYmM2Y2U3ZjI0YWRjNTk4M2VjNGUxIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.oo9QsgwivgWS4lx5R2tyCg0DNRkkE5FfqTdYujfRqYE"
TMDB_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
}

def main():
    # Initialize review_count and reviews in session_state if they don't exist
    if 'review_count' not in st.session_state:
        st.session_state.review_count = 0  # Default value is 0
    
    if 'reviews' not in st.session_state:
        st.session_state.reviews = {}  # Initialize reviews as an empty dictionary

    with st.sidebar:
        st.title("🎬 PixiePicks A.I.")
        page = st.radio("Menu", ["Recommendations", "Trending", "Offers"])
        st.markdown("---")
        st.write(f"👤 Profile: **{st.session_state.user_type or 'Guest'}**")

    if page == "Recommendations":
        recommendations_section(movies, similarity, st.session_state.user_type, KIDS_KEYWORDS, EXPLICIT_KEYWORDS, TMDB_API_KEY, TMDB_HEADERS)
    elif page == "Trending":
        trending_section(movies, similarity, st.session_state.user_type, KIDS_KEYWORDS, EXPLICIT_KEYWORDS, TMDB_API_KEY, TMDB_HEADERS)
    elif page == "Offers":
        offers_section(st.session_state.review_count)  # Now review_count and reviews are properly initialized


if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = True
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None

    if not st.session_state.logged_in:
        st.error("Please log in first")
    else:
        if not st.session_state.user_type:
            st.title("PixiePicks: Movie Recommendations and Reviews Platform 🎬🍿🥤")
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
