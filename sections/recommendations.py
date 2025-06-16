import streamlit as st
from sections.card.utils import display_movie_card  # Updated import from 'card/utils.py'

# Function to check if a movie is kid-friendly
def is_kid_friendly(tags, KIDS_KEYWORDS, EXPLICIT_KEYWORDS):
    if not isinstance(tags, str):
        return False
    tags_lower = tags.lower()
    return (any(keyword in tags_lower for keyword in KIDS_KEYWORDS) and
            not any(explicit in tags_lower for explicit in EXPLICIT_KEYWORDS))

# Recommendations section function
def recommendations_section(movies, similarity, user_type, KIDS_KEYWORDS, EXPLICIT_KEYWORDS, TMDB_API_KEY, TMDB_HEADERS):
    st.header("🎬 Personalized Recommendations")
    available_movies = movies[movies['tags'].apply(lambda x: is_kid_friendly(x, KIDS_KEYWORDS, EXPLICIT_KEYWORDS))] if user_type == "Kids" else movies
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
            if user_type == "Kids" and not is_kid_friendly(movie['tags'], KIDS_KEYWORDS, EXPLICIT_KEYWORDS):
                continue
            recommended_movies.append(movie)
            if len(recommended_movies) >= 5:
                break
        st.subheader("Recommended For You")
        for movie in recommended_movies:
            display_movie_card(movie, TMDB_API_KEY, TMDB_HEADERS)  # Pass TMDB_API_KEY and TMDB_HEADERS to display_movie_card
