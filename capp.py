import pickle
import streamlit as st
import requests

def fetch_poster(movie_id):
    # Fetch movie details from TMDb API
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkZjlmN2NmOTJhMmQzMTU2NjMwYzc0OGMxNTgxNWQwOCIsIm5iZiI6MTcyNzA5MjYzMS45NDIwMDAyLCJzdWIiOiI2NmYxNTc5NzZjM2I3YThkNjQ4ZGM1YWEiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.I9B0vN-DsOv0LRdhghegkIiL4GhTONOsSe-MZopmRO0",  # Replace with your actual API key
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_poster_url
    # Return a default image if no poster is found
    return "https://via.placeholder.com/500x750?text=No+Poster+Available"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies_names = []
    recommended_movies_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_names.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies_names, recommended_movies_posters

# Streamlit interface
st.header("Movie Recommendation System")

# Load movie list and similarity data from pickle files
movies = pickle.load(open(r'C:\Users\hp\Downloads\movie_recommendation _sys\fpro\movie_list.pkl', 'rb'))
similarity = pickle.load(open(r'C:\Users\hp\Downloads\movie_recommendation _sys\fpro\similarity.pkl', 'rb'))

# Extract movie titles for selection
movie_list = movies['title'].values

# Movie selection dropdown
selected_movie = st.selectbox(
    'Type or select a movie',
    movie_list
)

if st.button('Show Recommendations'):
    recommend_movie_name, recommend_movie_poster = recommend(selected_movie)

    # Display recommended movies
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommend_movie_name[0])
        st.image(recommend_movie_poster[0])
    with col2:
        st.text(recommend_movie_name[1])
        st.image(recommend_movie_poster[1])
    with col3:
        st.text(recommend_movie_name[2])
        st.image(recommend_movie_poster[2])
    with col4:
        st.text(recommend_movie_name[3])
        st.image(recommend_movie_poster[3])
    with col5:
        st.text(recommend_movie_name[4])
        st.image(recommend_movie_poster[4])
