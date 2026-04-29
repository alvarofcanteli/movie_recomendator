import streamlit as st
import pandas as pd
import requests
import sys
import os
from dotenv import load_dotenv

# app.py
# Interfaz visual del recomendador de películas.
# Construida con Streamlit.

# --- Load environment variables ---
load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w300'

# --- Add movierec to path so we can import recommender ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'movierec'))
from recommender import build_user_profile, content_score, collaborative_score, hybrid_score

# --- Page setup ---
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered")

# --- Load data ---
movies_table = pd.read_csv('data/movies_table.csv')
ratings_table = pd.read_csv('data/ratings_table.csv')
onboarding_movies = pd.read_csv('data/onboarding_movies.csv')

# --- Session state initialization ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'user_ratings' not in st.session_state:
    st.session_state.user_ratings = {}
if 'finished' not in st.session_state:
    st.session_state.finished = False
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'recs_shown' not in st.session_state:
    st.session_state.recs_shown = 10

# --- Function to get movie poster from TMDB ---
def get_poster(title):
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&language=en-US"
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    try:
        response = requests.get(url, headers=headers).json()
        if response['results']:
            poster_path = response['results'][0].get('poster_path')
            if poster_path:
                return TMDB_IMAGE_BASE + poster_path
    except:
        pass
    return None

def get_movie_details(title):
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&language=en-US"
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    try:
        response = requests.get(url, headers=headers).json()
        if response['results']:
            return response['results'][0]
    except:
        pass
    return None

# --- Header ---
st.title("🎬 Movie Recommender")
st.divider()

# --- Recommendations screen ---
if st.session_state.recommendations is not None:
    st.subheader("Here are your recommendations! 🎯")
    st.divider()

    cols_per_row = 5
    recs = st.session_state.recommendations.head(st.session_state.recs_shown)
    rows = [recs.iloc[i:i+cols_per_row] for i in range(0, len(recs), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, movie) in zip(cols, row.iterrows()):
            with col:
                poster_url = get_poster(movie['title'])
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.write("🎬")
                st.caption(movie['title'])
                with st.expander("More info"):
                    details = get_movie_details(movie['title'])
                    if details:
                        st.write(f"⭐ {details['vote_average']}/10")
                        st.write(f"📅 {details['release_date'][:4]}")
                        st.write(f"📖 {details['overview']}")
                    else:
                        st.write("No info available.")

    st.divider()
    if st.session_state.recs_shown < len(st.session_state.recommendations):
        if st.button("Show 10 more 🎬", use_container_width=True):
            st.session_state.recs_shown += 10
            st.rerun()

    st.divider()
    if st.button("Start over 🔄", use_container_width=True):
        st.session_state.current_index = 0
        st.session_state.user_ratings = {}
        st.session_state.finished = False
        st.session_state.recommendations = None
        st.session_state.recs_shown = 10
        st.rerun()

# --- Finished screen ---
elif st.session_state.finished:
    st.subheader("You're all set! 🎯")
    st.write(f"You rated **{len(st.session_state.user_ratings)}** movies.")

    if st.button("Get Recommendations 🎯", use_container_width=True):
        with st.spinner("Finding your perfect movies..."):
            user_profile = build_user_profile(st.session_state.user_ratings, movies_table)
            content_scores = content_score(user_profile, movies_table)
            collab_scores = collaborative_score(st.session_state.user_ratings, ratings_table, movies_table)
            st.session_state.recommendations = hybrid_score(content_scores, collab_scores)
        st.rerun()

# --- Onboarding screen ---
else:
    current = st.session_state.current_index
    ratings_done = len(st.session_state.user_ratings)

    if ratings_done >= 30 or current >= len(onboarding_movies):
        st.session_state.finished = True
        st.rerun()

    movie = onboarding_movies.iloc[current]

    st.caption(f"Ratings: {ratings_done} / 30")
    st.progress(ratings_done / 30)

    poster_url = get_poster(movie['title'])
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.write("🎬")
        st.subheader(movie['title'])

    st.divider()

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        rating = st.slider(
            label="Your rating",
            min_value=1,
            max_value=5,
            value=3,
            step=1
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Skip ⏭️", use_container_width=True):
            st.session_state.current_index += 1
            st.rerun()
    with col3:
        if st.button("Rate ⭐", use_container_width=True):
            st.session_state.user_ratings[movie['title']] = rating
            st.session_state.current_index += 1
            st.rerun()