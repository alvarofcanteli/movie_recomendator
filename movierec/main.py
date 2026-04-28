#---Importing used libraries------------------------
import pandas as pd
import json

def get_director(crew_str):
    for member in json.loads(crew_str):
        if member['job'] == 'Director':
            return member['name']
    return None


def main():
    

    #---Installing the datasets------------------------
    movies = pd.read_csv('data/tmdb_5000_movies.csv')
    credits = pd.read_csv('data/tmdb_5000_credits.csv')
    ml_ratings = pd.read_csv('data/ratings.csv')
    ml_links = pd.read_csv('data/links.csv')


    #---Exploration-----------------------------------
    # Movies
    print("=== MOVIES ===")
    print(movies.info())
    print(movies.head(10))

    # # Credits
    print("\n=== CREDITS ===")
    print(credits.info())
    print(credits.head(10))

    # # Raings
    print("\n=== RATINGS ===")
    print(ml_ratings.info())
    print(ml_ratings.head(10))


    # # Links
    print("\n=== LINKS ===")
    print(ml_links.info())
    print(ml_links.head(10))


    #----Dataset for website-------------------------
    '''For the website's dataset, three different tables will be required
    Firstly, a table with the movies ID, Genres, Director and Actors for each movie that is considered, this table is called movies_table
    Secondly, a table with the User's ID, Movie's ID and rating of the movie called ratings_table
    Lastly, a table with only the users called users_table'''


    # 1- Movies_table
    '''For creating the dataset with the infomration needed, different methods will be used depending on what
    For the genres and actors, regex is used because it is noticed that the same format is used, so str.findall will print everything,
    we have to limit the number of actors that are chosen to 5.'''

    movies['genres_parsed'] = movies['genres'].str.findall(r'"name": "([^"]+)"').apply(json.dumps)
    credits['actors_parsed'] = credits['cast'].str.findall(r'"name": "([^"]+)"').apply(lambda x: json.dumps(x[:5]))

    '''The next step we have is choosing the director.
    The director format isn't consistent so a new method called json.loads() is used.
    This method  converts the JSON string into a real Python list of dictionaries
    so that looping through them and finding the member whose job is "Director" is possible'''


    credits['director'] = credits['crew'].apply(get_director) # New column called director with the director of each film

    '''And finally, we must join all these columns, 
    From the dataset movies, we only need the movies id, title and genres_parsed,
    From the credits one, we only need movie_id, director and actor_parsed.
    They will be joined by the movie id, in the movies dataset it is "id" while on credits is "movie_id"
    so they will be joined, and then dropped the "movie_id" column so that we only have the "id" column
    Finally, they will be renamed for convenience
    '''
    movies_table = movies[['id', 'title', 'genres_parsed']].merge(
        credits[['movie_id', 'director', 'actors_parsed']],
        left_on='id', #On the movies dataset, the column is named id
        right_on='movie_id' #On the credits dataset, the column is named movie_id
    ).drop(columns='movie_id') # We only need one column (ID)

    movies_table = movies_table.rename(columns={
        'genres_parsed': 'genres',
        'actors_parsed': 'actors'
    }) #Renaming for convenience

    print("=== MOVIES TABLE ===")
    print(movies_table.info())
    print(movies_table.head(5))


    # 2- Users_table
    '''What must be done is simply to keep the userId column only,
    drop the duplicates and reset index so that the user with ID 1 is in row 1, ID 2 in row 2...'''


    users_table = ml_ratings[['userId']].drop_duplicates().reset_index(drop=True)

    print("\n=== USERS_TABLE ===")
    print(users_table.info())
    print(users_table.head(10))
 

    # 3- Ratings_table

    '''For this table, a couple of things must be done, 
    ratings.csv and tmbd_5000_movies.csv had different movies IDs,
    ratings.csv knew movies by MovieLens ID,
    while tmdb_5000_movies.csv knew movies by TMBD IDs,
    so since ID's are different, a join must be done to switch the IDs with links.csv that has both IDs.
    The join would join then merge ml_links and ml_ratings on the key movieID,
    Making ratings_table have the columns UserID, rating and both IDs,
    Then keeping the tmdbId and dropping the original MovieLens movieId is done,
    and finally, dropping NA values and transforming into integers is the final step for this table. '''


    ratings_table = ml_ratings.merge(ml_links[['movieId', 'tmdbId']], on='movieId') #Merging
    ratings_table = ratings_table[['userId', 'tmdbId', 'rating']] #Keeping important columns
    ratings_table = ratings_table.rename(columns={'tmdbId': 'movieId'}) #Renaming for convenience
    ratings_table = ratings_table.dropna() #Dropping NA values
    ratings_table['movieId'] = ratings_table['movieId'].astype(int) #Transforming to integer

    print("=== RATINGS TABLE ===")
    print(ratings_table.info())
    print(ratings_table.head(10))

    #----Dataset for website-------------------------

    '''Finally, the tables must be exported so that they can be worked on in another script,
    each will be exported to a csv and downloaded directly to the directory were the work is being done.'''
    movies_table.to_csv('movies_table.csv', index=False)
    users_table.to_csv('users_table.csv', index=False)
    ratings_table.to_csv('ratings_table.csv', index=False)

    print("\n=== TABLES EXPORTED ===")
if __name__ == "__main__" :
    main()
