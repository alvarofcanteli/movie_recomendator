import pandas as pd
from movierec.onboarding import compute_onboarding_movies


# ---------------------------
# Sample data
# ---------------------------
def sample_movies():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "title": ["Movie A", "Movie B", "Movie C"]
    })


def sample_ratings():
    return pd.DataFrame({
        "userId": [1]*60 + [2]*60 + [3]*10,
        "movieId": [1]*60 + [2]*60 + [3]*10,
        "rating": [5]*60 + [4]*60 + [3]*10
    })


# ---------------------------
# Test structure
# ---------------------------
def test_onboarding_output_structure():
    movies = sample_movies()
    ratings = sample_ratings()

    result = compute_onboarding_movies(movies, ratings, min_ratings=50)

    assert "title" in result.columns #Makes sure that the dataframe has "title" in the columns
    assert "num_ratings" in result.columns #Makes sure that the dataframe has "num_ratings" in the columns
    assert "mean_rating" in result.columns #Makes sure that the dataframe has "mean_rating" in the columns


# ---------------------------
# Test filtering (min ratings)
# ---------------------------
def test_min_ratings_filter():
    movies = sample_movies()
    ratings = sample_ratings()

    result = compute_onboarding_movies(movies, ratings, min_ratings=50)

    # Movie C has only 10 ratings → should be excluded
    assert "Movie C" not in result["title"].values #Makes sure that if the movie doesn't have enough ratings for it, it won't be included


# ---------------------------
# Test ranking (mean rating)
# ---------------------------
def test_sorted_by_mean_rating():
    movies = sample_movies()
    ratings = sample_ratings()

    result = compute_onboarding_movies(movies, ratings, min_ratings=50)

    # Movie A has rating 5, Movie B has rating 4 → A should be first
    assert result.iloc[0]["title"] == "Movie A" #Makes sure that the movie with the higher rating is selected first


# ---------------------------
# Test limit (top N)
# ---------------------------
def test_top_limit():
    movies = pd.DataFrame({
        "id": list(range(100)),
        "title": [f"Movie {i}" for i in range(100)]
    })

    ratings = pd.DataFrame({
        "userId": [1]*100,
        "movieId": list(range(100)),
        "rating": [5]*100
    })

    result = compute_onboarding_movies(movies, ratings, min_ratings=1)

    assert len(result) <= 50 #Makes sure that the results contains at most 50 movies


# ---------------------------
# Test empty case
# ---------------------------
def test_no_movies_pass_filter():
    movies = sample_movies()

    # All movies have very few ratings
    ratings = pd.DataFrame({
        "userId": [1, 2, 3],
        "movieId": [1, 2, 3],
        "rating": [5, 4, 3]
    })

    result = compute_onboarding_movies(movies, ratings, min_ratings=50)

    assert result.empty #Makes sure that when no movies achieve the minimum number of ratings, the dataframe is empty