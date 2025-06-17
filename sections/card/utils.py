import streamlit as st
import requests
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import mysql.connector
from mysql.connector import Error

def create_request_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

# MySQL database connection function
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Your MySQL host
            database="movie_db",  # Your database name
            user="root",  # Your MySQL username
            password="root"  # Your MySQL password
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to fetch movie details from TMDB API
def fetch_movie_details(title, api_key, headers):
    session = create_request_session()
    try:
        # Search for the movie
        search_url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": api_key,
            "query": title,
            "language": "en-US"
        }
        response = session.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        if results:
            return results[0]
        return None
    except Exception as e:
        st.warning(f"Could not fetch details for {title}")
        return None

# Function to fetch poster from TMDB API
def fetch_poster(movie_id, TMDB_API_KEY, TMDB_HEADERS):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?language=en-US"
        response = requests.get(url, headers=TMDB_HEADERS)  # Pass TMDB_HEADERS here
        response.raise_for_status()
        data = response.json()
        poster_path = data['posters'][0]['file_path'] if 'posters' in data and len(data['posters']) > 0 else None
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        # Return a default image if poster can't be fetched
        return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

# Function to store review in MySQL database
def store_review(movie_id, movie_title, review_text):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            insert_query = "INSERT INTO movie_reviews (movie_id, movie_title, review_text) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (movie_id, movie_title, review_text))
            connection.commit()
            st.success("Thanks for your review!")
        except Error as e:
            print(f"Error inserting review: {e}")
            st.error("Failed to submit your review.")
        finally:
            cursor.close()
            connection.close()

# Function to fetch reviews for a movie
def fetch_reviews(movie_id):
    connection = connect_to_db()
    reviews = []
    if connection:
        cursor = connection.cursor()
        try:
            select_query = "SELECT review_text FROM movie_reviews WHERE movie_id = %s"
            cursor.execute(select_query, (movie_id,))
            reviews = cursor.fetchall()  # Get all reviews for the movie
        except Error as e:
            print(f"Error fetching reviews: {e}")
            st.error(f"Failed to fetch reviews: {e}")
        finally:
            cursor.close()
            connection.close()
    return reviews

# Function to display movie card with details
def display_movie_card(movie, api_key, headers):
    try:
        movie_details = fetch_movie_details(movie['title'], api_key, headers)
        
        if movie_details:
            col1, col2 = st.columns([1, 2])
            with col1:
                poster_path = movie_details.get('poster_path')
                if poster_path:
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    try:
                        session = create_request_session()
                        response = session.get(poster_url, stream=True)
                        if response.status_code == 200:
                            st.image(poster_url, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/500x750?text=No+Poster")
                    except Exception:
                        st.image("https://via.placeholder.com/500x750?text=No+Poster")
                else:
                    st.image("https://via.placeholder.com/500x750?text=No+Poster")
            
            with col2:
                st.subheader(movie['title'])
                st.write(f"**Rating:** {movie_details.get('vote_average', 'N/A')}/10")
                st.write(f"**Overview:** {movie_details.get('overview', 'Not available')}")
                st.write(f"**Tags:** {movie['tags']}")
                
                # Add review system
                movie_id = str(movie_details.get('id', movie['title']))
                
                # Initialize review in session state if not exists
                if 'reviews' not in st.session_state:
                    st.session_state.reviews = {}
                
                # Review input
                user_review = st.text_area(
                    "Write your review:",
                    key=f"review_input_{movie_id}",
                    value=st.session_state.reviews.get(movie_id, "")
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Submit Review", key=f"submit_{movie_id}"):
                        if user_review.strip():
                            st.session_state.reviews[movie_id] = user_review
                            if 'review_count' not in st.session_state:
                                st.session_state.review_count = 0
                            st.session_state.review_count += 1
                            st.success("Review submitted successfully!")
                
                with col2:
                    if st.button("Clear Review", key=f"clear_{movie_id}"):
                        if movie_id in st.session_state.reviews:
                            del st.session_state.reviews[movie_id]
                            st.session_state.review_count = max(0, st.session_state.review_count - 1)
                            st.success("Review cleared!")
                            st.rerun()
                
                # Display existing review
                if movie_id in st.session_state.reviews:
                    st.write("**Your Review:**")
                    st.info(st.session_state.reviews[movie_id])
                    
        else:
            st.warning(f"Could not load details for {movie['title']}")
            
    except Exception as e:
        st.warning(f"Error displaying movie card for {movie['title']}")
