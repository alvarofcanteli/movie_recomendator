# 🎬 Movie Recommender

A hybrid movie recommender system built with Python that combines content-based and collaborative filtering.

## Requirements
- Python 3.11
- conda

## Installation

1. Clone the repository
git clone https://github.com/alvarofcanteli/movie_recomendator

2. Create and activate the conda environment
conda create -n movie_recomendator python=3.11
conda activate movie_recomendator

3. Install dependencies
pip install pandas streamlit requests python-dotenv

4. Add the datasets
Place the following files inside the data/ folder:
- tmdb_5000_movies.csv
- tmdb_5000_credits.csv
- ratings.csv
- links.csv

5. Configure your TMDB API key
Create a .env file in the root folder (use .env.example as reference):
TMDB_API_KEY=your_api_key_here

6. Generate the data tables
python mypackage/main.py
python mypackage/onboarding.py

## Usage
streamlit run app/app.py