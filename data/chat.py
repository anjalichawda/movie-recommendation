import streamlit as st
import pickle
import pandas as pd
import requests

# Load data
movies = pickle.load(open('movies_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# TMDB API
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=YOUR_API_KEY_HERE&language=en-US"
        response = requests.get(url)
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
    except:
        return "https://via.placeholder.com/300x450?text=No+Image"

# Recommend function
def recommend(movie, profile):
    filtered_movies = movies[movies['is_kids'] == (profile == "Kids")].reset_index(drop=True)
    
    try:
        idx = filtered_movies[filtered_movies['title'] == movie].index[0]
        distances = similarity[idx]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_titles = []
        recommended_posters = []
        for i in movie_list:
            recommended_titles.append(filtered_movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(filtered_movies.iloc[i[0]].movie_id))
        return recommended_titles, recommended_posters
    except:
        return [], []

# Streamlit UI
st.set_page_config(page_title="CineMatch Pro", layout="wide")
st.title("🎬 CineMatch Pro - Personalized Movie Recommendations")

# Profile Selection
profile = st.selectbox("Choose Your Profile", ["Kids", "Adults"])

# Movie Selection (filtered list)
filtered_titles = movies[movies['is_kids'] == (profile == "Kids")]['title'].tolist()
selected_movie = st.selectbox("Select a Movie", filtered_titles)

# Show Recommendations
if st.button("Get Recommendations"):
    titles, posters = recommend(selected_movie, profile)
    if titles:
        st.subheader("📽️ Recommended for You:")
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                st.caption(titles[i])
    else:
        st.error("No recommendations found. Try a different movie.")

# Review Section
st.markdown("## 📝 Leave a Review")
with st.form("review_form"):
    user_review = st.text_area("What did you think about the movie?")
    submit_review = st.form_submit_button("Submit Review")
    if submit_review:
        st.success("Thanks for your feedback! 🌟")

# Personalized Offers
st.markdown("## 🎁 Special Offers Just for You")

if profile == "Kids":
    st.info("✨ **Kids Special Offer:** Enjoy ad-free cartoons all weekend! Use code `KIDSFUN` 🎉")
    st.image("https://i.imgur.com/1Jq6HhG.png", width=400)
else:
    st.success("🎬 **Adults Offer:** Unlock 1 month premium free with code `MOVIELOVE` 🍿")
    st.image("https://i.imgur.com/t2KjB8H.png", width=400)
