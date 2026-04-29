import pandas as pd

'''
onboarding.py
Selecciona las 20 películas más adecuadas para el onboarding de nuevos usuarios.
Criterios: películas con muchas valoraciones y media de rating alta,
presentes en ambos datasets (TMDB y MovieLens).
'''

MIN_RATINGS = 50


def compute_onboarding_movies(movies_table, ratings_table, min_ratings=MIN_RATINGS):
    # Count ratings and mean
    movie_stats = ratings_table.groupby('movieId').agg(
        num_ratings=('rating', 'count'),
        mean_rating=('rating', 'mean')
    ).reset_index()

    # Filter popular movies
    popular_movies = movie_stats[movie_stats['num_ratings'] >= min_ratings]

    # Merge with movie titles
    popular_movies = popular_movies.merge(
        movies_table[['id', 'title']],
        left_on='movieId',
        right_on='id'
    ).drop(columns='id')

    # Sort and select top 50
    onboarding_movies = popular_movies.sort_values(
        'mean_rating', ascending=False
    ).head(50)

    return onboarding_movies


def main():
    movies_table = pd.read_csv('data/movies_table.csv')
    ratings_table = pd.read_csv('data/ratings_table.csv')

    onboarding_movies = compute_onboarding_movies(movies_table, ratings_table)

    print(onboarding_movies[['title', 'num_ratings', 'mean_rating']].to_string(index=False))

    onboarding_movies[['title', 'mean_rating']].to_csv(
        'data/onboarding_movies.csv',
        index=False
    )

    print("\nOnboarding movies saved to data/onboarding_movies.csv")


if __name__ == "__main__":
    main()