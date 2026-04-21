import pandas as pd

'''
onboarding.py
Selecciona las 20 películas más adecuadas para el onboarding de nuevos usuarios.
Criterios: películas con muchas valoraciones y media de rating alta,
presentes en ambos datasets (TMDB y MovieLens).
'''

# Load tables built by main.py
movies_table = pd.read_csv('data/movies_table.csv')
ratings_table = pd.read_csv('data/ratings_table.csv')

# Count number of ratings and mean rating per movie
movie_stats = ratings_table.groupby('movieId').agg( #Group every row by movie, and for every group we calculate two things at the same time:
    num_ratings=('rating', 'count'), #How many valortaions it has
    mean_rating=('rating', 'mean') #The mean of those valorations
).reset_index() #Transforms the index into a normal column 

# Keep only movies with at least 50 ratings (enough to be reliable)
MIN_RATINGS = 50
popular_movies = movie_stats[movie_stats['num_ratings'] >= MIN_RATINGS] #We filter to only remain with the movies that have num_ratings bigger or equal than 50

# Merge with movies_table to get the title
popular_movies = popular_movies.merge(movies_table[['id', 'title']], left_on='movieId', right_on='id').drop(columns='id') #A merge is performed betweeen our filter data based on rating with the dataset containing the relevant info of these movies

# Sort by mean rating and select top 50
onboarding_movies = popular_movies.sort_values('mean_rating', ascending=False).head(50) #sort_values(...) orders from higher to lower mean 
print(onboarding_movies[['title', 'num_ratings', 'mean_rating']].to_string(index=False))

# Export onboarding movies to CSV
onboarding_movies[['title', 'mean_rating']].to_csv('data/onboarding_movies.csv', index=False)
print("\nOnboarding movies saved to data/onboarding_movies.csv")