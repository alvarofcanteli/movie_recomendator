import pandas as pd
import json
from movierec.recommender import (
    build_user_profile,
    content_score,
    collaborative_score,
    hybrid_score
)


# ---------------------------
# Sample data
# ---------------------------
def sample_movies():
    return pd.DataFrame({
        "id": [1, 2],
        "title": ["Movie A", "Movie B"],
        "genres": [json.dumps(["Action"]), json.dumps(["Drama"])],
        "director": ["Director X", "Director Y"],
        "actors": [json.dumps(["Actor1", "Actor2"]), json.dumps(["Actor3"])]
    })


def sample_ratings():
    return pd.DataFrame({
        "userId": [1, 1, 2, 2],
        "movieId": [1, 2, 1, 2],
        "rating": [5, 3, 4, 2]
    })


# ---------------------------
# Test build_user_profile
# ---------------------------
def test_build_user_profile():
    movies = sample_movies()
    user_ratings = {"Movie A": 5}  # weight = +2

    profile = build_user_profile(user_ratings, movies)

    assert profile["Action"] == 4 #Makes sure that the grade given to the genre is 4
    assert profile["Director X"] == 3 #Makes sure the grade given to the director is 3
    assert profile["Actor1"] == 2 #Makes sure the grade given to the actor is 2


def test_build_user_profile_missing_movie():
    movies = sample_movies()
    profile = build_user_profile({"Unknown": 5}, movies)

    assert profile == {} #Makes sure that a profile is being created even if it misses a movie.


# ---------------------------
# Test content_score
# ---------------------------
def test_content_score_structure():
    movies = sample_movies()
    profile = {"Action": 4}

    scores = content_score(profile, movies)

    assert "content_score" in scores.columns #Makes sure that the scores are inside the column
    assert len(scores) == 2 #makes sures that there are only 2 datas inside the scores which are profile and movies


def test_content_score_ranking():
    movies = sample_movies()
    profile = {"Action": 4}

    scores = content_score(profile, movies)

    assert scores.iloc[0]["title"] == "Movie A" #Makes sure that the profile coincides with what it should


# ---------------------------
# Test collaborative_score
# ---------------------------
def test_collaborative_score_runs():
    movies = sample_movies()
    ratings = sample_ratings()

    user_ratings = {"Movie A": 5}

    result = collaborative_score(user_ratings, ratings, movies)

    assert isinstance(result, pd.DataFrame) #makes sure that the results are a pandas dataframe


def test_collaborative_score_empty():
    movies = sample_movies()
    ratings = sample_ratings()

    result = collaborative_score({"Unknown": 5}, ratings, movies)

    assert result.empty #makes sure that if there is no movie it will return an empty result


# ---------------------------
# Test hybrid_score
# ---------------------------
def test_hybrid_score_structure():
    content = pd.DataFrame({
        "id": [1, 2],
        "title": ["A", "B"],
        "content_score": [0.8, 0.2]
    })

    collab = pd.DataFrame({
        "id": [1, 2],
        "title": ["A", "B"],
        "collab_score": [4, 2]
    })

    result = hybrid_score(content, collab)

    assert "final_score" in result.columns #Makes sure that the final result is inside the collumn


def test_hybrid_score_ranking():
    content = pd.DataFrame({
        "id": [1, 2],
        "title": ["A", "B"],
        "content_score": [1, 0]
    })

    collab = pd.DataFrame({
        "id": [1, 2],
        "title": ["A", "B"],
        "collab_score": [5, 1]
    })

    result = hybrid_score(content, collab)

    assert result.iloc[0]["title"] == "A" #makes sure that in the given example the title in the iloc would be "A"


def test_hybrid_score_no_div_zero():
    content = pd.DataFrame({
        "id": [1, 2],
        "title": ["A", "B"],
        "content_score": [1, 1]
    })

    collab = pd.DataFrame({
        "id": [1, 2],
        "title": ["A", "B"],
        "collab_score": [3, 3]
    })

    result = hybrid_score(content, collab)

    assert not result["final_score"].isna().any() #Makes sure that the final result doesn't contain any 0 or NaN values