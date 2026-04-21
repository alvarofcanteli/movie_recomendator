import streamlit as st
import pandas as pd
import requests
import os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''
app.py
Interfaz visual del recomendador de películas.
Construida con Streamlit.
'''

# --- Configuration ---
TMDB_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MmUzMWFkMmU4NjM3ZDcwMjgyNDhmZDVjYmM5OWI5MyIsIm5iZiI6MTc3Njc4MjI0Ni41MTIsInN1YiI6IjY5ZTc4YmE2N2RlYzE0YWI1OGQxOTUxMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Xcg_eK6lZ8-NX8qEVJoqYPSaxtyq-k1icKt2Z2h9mnM'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w300'

# --- Page setup ---
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# --- Load onboarding movies ---
movies = pd.read_csv('data/onboarding_movies.csv')