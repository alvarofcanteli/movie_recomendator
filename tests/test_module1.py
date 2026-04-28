import pandas as pd
import json
from movierec.main import get_director


# ---------------------------
# Test get_director
# ---------------------------
def test_get_director_found():
    crew = json.dumps([
        {"job": "Director", "name": "James Cameron"},
        {"job": "Producer", "name": "John"}
    ])
    assert get_director(crew) == "James Cameron" #Checks that the director coincidies


def test_get_director_not_found():
    crew = json.dumps([
        {"job": "Producer", "name": "Someone"}
    ])
    assert get_director(crew) is None #Makes sure that if there isn't a director python realises it


# ---------------------------
# Test genre parsing (JSON version)
# ---------------------------
def test_genres_parsing_json():
    genres = '[{"name": "Action"}, {"name": "Comedy"}]'

    parsed = pd.Series([genres]) \
        .str.findall(r'"name": "([^"]+)"') \
        .apply(json.dumps)[0]

    # Now it's a JSON string → convert back to list
    parsed_list = json.loads(parsed)

    assert parsed_list == ["Action", "Comedy"] #Makes sure that the themes coincides with what it should


# ---------------------------
# Test actors limit (JSON version)
# ---------------------------
def test_actors_limit_json():
    df = pd.DataFrame({
        "cast": ['[{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}, {"name": "F"}]']
    })

    df['actors_parsed'] = df['cast'] \
        .str.findall(r'"name": "([^"]+)"') \
        .apply(lambda x: json.dumps(x[:5]))

    actors_list = json.loads(df['actors_parsed'][0])

    assert len(actors_list) == 5 #Making sure that the number of actors is correct


# ---------------------------
# Test movies_table merge (JSON version)
# ---------------------------
def test_movies_table_merge_json():
    movies = pd.DataFrame({
        "id": [1],
        "title": ["Movie A"],
        "genres_parsed": [json.dumps(["Action"])]
    })

    credits = pd.DataFrame({
        "movie_id": [1],
        "director": ["Director A"],
        "actors_parsed": [json.dumps(["Actor1", "Actor2"])]
    })

    movies_table = movies.merge(
        credits,
        left_on="id",
        right_on="movie_id"
    ).drop(columns="movie_id")

    movies_table = movies_table.rename(columns={
        "genres_parsed": "genres",
        "actors_parsed": "actors"
    })

    assert "genres" in movies_table.columns
    assert json.loads(movies_table.iloc[0]["actors"]) == ["Actor1", "Actor2"] #Makes sure that the actors have been saved into the movie_table


# ---------------------------
# Test users_table
# ---------------------------
def test_users_table_unique():
    ratings = pd.DataFrame({
        "userId": [1, 1, 2, 3]
    })

    users_table = ratings[['userId']].drop_duplicates().reset_index(drop=True)

    assert list(users_table['userId']) == [1, 2, 3] #Makes sure that the same id isn't repeated


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

    assert ratings_table.iloc[0]["movieId"] == 100 #to check that the ratings table is correct.