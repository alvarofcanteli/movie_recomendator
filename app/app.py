import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# app.py
# Interfaz visual del recomendador de películas.
# Construida con Streamlit.

# --- Configuration ---
load_dotenv()  # loads the .env file
TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # reads the key from .env
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w300'

# --- Page setup ---
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered")

# --- Load onboarding movies ---
movies = pd.read_csv('data/onboarding_movies.csv')  # full pool of 50 movies

# --- Session state initialization ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0  # which movie we are on in the pool
if 'user_ratings' not in st.session_state:
    st.session_state.user_ratings = {}  # dictionary of title: rating
if 'finished' not in st.session_state:
    st.session_state.finished = False  # whether the user has finished

# --- Function to get movie poster from TMDB ---
def get_poster(title):
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&language=en-US"
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    response = requests.get(url, headers=headers).json()
    if response['results']:
        poster_path = response['results'][0].get('poster_path')
        if poster_path:
            return TMDB_IMAGE_BASE + poster_path
    return None

# --- Header ---
st.title("🎬 Movie Recommender")
st.divider()

# --- Finished screen ---
if st.session_state.finished:
    st.subheader("You're all set! 🎯")
    st.write(f"You rated **{len(st.session_state.user_ratings)}** movies.")
    st.write("Here are your ratings:")
    st.write(st.session_state.user_ratings)
    if st.button("Get Recommendations 🎯", use_container_width=True):
        st.success("Recommendations coming soon!")

# --- Onboarding screen ---
else:
    current = st.session_state.current_index
    ratings_done = len(st.session_state.user_ratings)  # only real ratings, skips don't count

    # Check finish conditions: 30 ratings reached or pool exhausted
    if ratings_done >= 30 or current >= len(movies):
        st.session_state.finished = True
        st.rerun()

    movie = movies.iloc[current]

    # Progress bar based on real ratings only
    st.caption(f"Ratings: {ratings_done} / 30")
    st.progress(ratings_done / 30)

    # Poster and title
    poster_url = get_poster(movie['title'])
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.write("🎬")
        st.subheader(movie['title'])

    st.divider()

    # Slider for rating
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        rating = st.slider(
            label="Your rating",
            min_value=1,
            max_value=5,
            value=3,
            step=1
        )

    # Buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Skip ⏭️", use_container_width=True):
            st.session_state.current_index += 1  # skip does not count as rating
            st.rerun()
    with col3:
        if st.button("Rate ⭐", use_container_width=True):
            st.session_state.user_ratings[movie['title']] = rating  # save rating
            st.session_state.current_index += 1
            st.rerun()