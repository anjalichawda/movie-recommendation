import streamlit as st
import requests

# Function to fetch movie details from TMDB API
def fetch_movie_details(movie_id, TMDB_API_KEY, TMDB_HEADERS):
    try:
        # Debugging: Print movie_id to ensure it's valid
        print(f"Fetching details for movie_id: {movie_id}")
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        response = requests.get(url, headers=TMDB_HEADERS, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Debugging: Check the full response to verify the structure
        data = response.json()
        print("Fetched movie details:", data)  # Debugging output

        return {
            'overview': data.get('overview', 'No description available'),  # Default if overview is missing
            'runtime': data.get('runtime', 'N/A'),
            'genres': data.get('genres', []),
            'vote_average': data.get('vote_average', 'N/A')
        }
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return None

# Function to fetch movie poster
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data['posters'][0]['file_path'] if 'posters' in data and len(data['posters']) > 0 else None
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

# Function to display movie card with details
def display_movie_card(movie, TMDB_API_KEY, TMDB_HEADERS):
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            try:
                poster = fetch_poster(movie['movie_id'])  # Fetch the poster using movie_id
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/500x750?text=Poster+Not+Available")
            except Exception as e:
                st.image("https://via.placeholder.com/500x750?text=Poster+Not+Available")
                st.error(f"Error loading poster: {str(e)}")
        
        with col2:
            st.subheader(movie['title'])
            details = fetch_movie_details(movie['movie_id'], TMDB_API_KEY, TMDB_HEADERS)  # Fetch movie details
            if details:
                # Only display the description if it's available
                st.caption(f"{details.get('runtime', 'N/A')} min | {', '.join([g['name'] for g in details.get('genres', [])])} | ★ {details.get('vote_average', 'N/A')}")
                st.write(details.get('overview', 'No description available'))  # Default if overview is missing

            # Review box
            review_key = f"review_{movie['title']}"
            submit_key = f"btn_{movie['title']}"
            expander_key = f"expander_{movie['title']}"
            if expander_key not in st.session_state:
                st.session_state[expander_key] = True  # Default to open

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
