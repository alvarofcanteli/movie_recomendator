from movierec.main import get_director
import pandas as pd

#----------------------------
#Test to get director
#----------------------------

#Case where there is a director
def test_get_director_found():
    crew = '[{"job": "Director", "name": "James Cameron"}, {"job": "Producer", "name": "John"}]'
    assert get_director(crew) == "James Cameron"

#Case where there isn't a director
def test_get_director_not_found():
    crew = '[{"job": "Producer", "name": "Someone"}]'
    assert get_director(crew) is None

# ---------------------------
# Test genre parsing
# ---------------------------
def test_genres_parsing():
    genres = '[{"name": "Action"}, {"name": "Comedy"}]'
    parsed = pd.Series([genres]).str.findall(r'"name": "([^"]+)"')[0]

    assert parsed == ["Action", "Comedy"] #Checks taht in the example there are 2 genres: Comedy and action


# ---------------------------
# Test actors limit
# ---------------------------
def test_actors_limit():
    df = pd.DataFrame({
        "cast": ['[{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}, {"name": "F"}]']
    })

    df['actors_parsed'] = df['cast'].str.findall(r'"name": "([^"]+)"')
    df['actors_parsed'] = df['actors_parsed'].apply(lambda x: x[:5])

    assert len(df['actors_parsed'][0]) == 5 #checks that there are 5 actors since it is the quantity in the example


# ---------------------------
# Test movies_table merge
# ---------------------------
def test_movies_table_merge():
    movies = pd.DataFrame({
        "id": [1],
        "title": ["Movie A"],
        "genres_parsed": [["Action"]]
    })

    credits = pd.DataFrame({
        "movie_id": [1],
        "director": ["Director A"],
        "actors_parsed": [["Actor1", "Actor2"]]
    })

    movies_table = movies.merge(
        credits,
        left_on="id",
        right_on="movie_id"
    ).drop(columns="movie_id")

    assert "director" in movies_table.columns
    assert movies_table.iloc[0]["director"] == "Director A" #Checks that the Director is insided the newly merged function


# ---------------------------
# Test users_table
# ---------------------------
def test_users_table_unique():
    ratings = pd.DataFrame({
        "userId": [1, 1, 2, 3]
    })

    users_table = ratings[['userId']].drop_duplicates().reset_index(drop=True)

    assert list(users_table['userId']) == [1, 2, 3] #Checks that the user's id coincide and that it dropped the dupplicate since you don't want the same user id to appear twice


# ---------------------------
# Test ratings_table
# ---------------------------
def test_ratings_table():
    ratings = pd.DataFrame({
        "userId": [1],
        "movieId": [10],
        "rating": [4.5]
    })

    links = pd.DataFrame({
        "movieId": [10],
        "tmdbId": [100]
    })

    ratings_table = ratings.merge(links, on="movieId")
    ratings_table = ratings_table[['userId', 'tmdbId', 'rating']]
    ratings_table = ratings_table.rename(columns={'tmdbId': 'movieId'})
    ratings_table = ratings_table.dropna()
    ratings_table['movieId'] = ratings_table['movieId'].astype(int)

    assert ratings_table.iloc[0]["movieId"] == 100 #Checks that the movie rating in the link imported coincides to check that the ratings table is correct.