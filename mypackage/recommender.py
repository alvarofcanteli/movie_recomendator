# =================================================================================
#SIMULATED USER INPUT FOR TESTING
user_ratings = {
    'The Shawsank Redemption': 5,
    'The Dark Knight': 5,
    'Inglourious Basterds': 5,
    'Rear Window': 4,
    'Pulp Fiction': 4,
    'Gladiator' : 4,
    'Forrest Gump' : 4,
    'After Hours' : 4,
    'Primal Fear' : 4,
    'Little Miss Sunshine': 4,
    'Joker' : 4,
    'Deads Poets Society' : 3,
    'Sully' : 3,
    'The Usual Suspects' : 3,
    'Superbad' : 3,
    'The Breakfast Club' : 3,
    'American Psycho' : 3,
    'Fargo' : 3,
    'The Dark Knight Rises' : 5,
    'Batman Begins' : 3
 }


# =================================================================================
import pandas as pd
import json

#----Loading the tables--------------------------
movies_table = pd.read_csv('movies_table.csv')
ratings_table = pd.read_csv('ratings_table.csv')
users_table = pd.read_csv('users_table.csv')


#----Step 1: Build user profile------------------
'''This function takes the user ratings and the movies table and builds a profile.
For each rated movie, it finds its genres, director and actors in movies_table.
It subtracts 3 from the rating to get a weight (+2, +1, 0, -1, -2).
Then it multiplies each feature by its weight and the corresponding importance (genre=2, director=1.5, actor=1).
Finally it averages each feature to get the profile.'''

def build_user_profile(user_ratings, movies_table):
    profile = {}
    counts = {}
    

    for title, rating in user_ratings.items():
        weight = rating - 3 #Substract 3 for convenience
        movie = movies_table[movies_table['title'] == title] # Find the row in movies_table where the title matches the current movie


        if movie.empty:
            continue #We iterate in movie_table. If user_rating movie ins't in movie_table, continue

        # Genres
        genres = json.loads(movie['genres'].values[0]) # A list is created with all the genres of each movie
        for genre in genres: # Iteration over the list for each genre
            profile[genre] = profile.get(genre, 0) + weight * 2 # We are creating keys that are each genre, and summing the weight (rating-3) * 2 
            counts[genre] = counts.get(genre, 0) + 1 # We are counting how many times each genre appears for the mean later

        # Director
        director = movie['director'].values[0] 
        if pd.notna(director): # We are doing the same, but without iterating and checking there is a director 
            profile[director] = profile.get(director, 0) + weight * 1.5
            counts[director] = counts.get(director, 0) + 1

        # Actors
        actors = json.loads(movie['actors'].values[0])
        for actor in actors: #Same as genres but actors
            profile[actor] = profile.get(actor, 0) + weight * 1
            counts[actor] = counts.get(actor, 0) + 1

    # Average
    for key in profile:
        profile[key] = profile[key] / counts[key] #Now we calculate the average, the total sum divided by the total number of times it appears

    return profile

user_profile = build_user_profile(user_ratings, movies_table)
print("\n ===USER PROFILE===")
print(user_profile)



#----Step 2: Content-based scoring---------------
'''This function scores every movie in movies_table based on how much it matches the user profile.
For each movie, it looks at its genres, director and actors and checks if they appear in the profile.
If they do, it adds profile[feature] * weight to the score.
Finally it divides by the number of features found to normalize the score.'''

def content_score(user_profile, movies_table):
    scores = []

    for _, row in movies_table.iterrows():
        score = 0
        total = 0  # Total features of the movie

        # Genres
        genres = json.loads(row['genres'])
        for genre in genres:
            if genre in user_profile:
                score += user_profile[genre] * 2
            total += 1  # Count all genres, not just matching ones

        # Director
        if pd.notna(row['director']):
            if row['director'] in user_profile:
                score += user_profile[row['director']] * 1.5
            total += 1  # Count director always

        # Actors
        actors = json.loads(row['actors'])
        for actor in actors:
            if actor in user_profile:
                score += user_profile[actor] * 1
            total += 1  # Count all actors

        if total > 0:
            score = score / total

        scores.append({'id': row['id'], 'title': row['title'], 'content_score': score})

    return pd.DataFrame(scores).sort_values('content_score', ascending=False)

content_scores = content_score(user_profile, movies_table)
print("\n ===CONTENT SCORES===")
print(content_scores.head(10))



#----Step 3: Collaborative filtering------------
'''This function finds users similar to the new user based on how they rated the same movies.
It normalizes ratings by subtracting each user's mean to avoid bias from generous or strict raters.
Then it calculates similarity using 1 / (1 + mean_difference).
Finally it scores unseen movies using a weighted average of similar users' ratings.'''

def collaborative_score(user_ratings, ratings_table, movies_table):
    
    # Convert user_ratings titles to tmdb ids
    user_ratings_id = {}
    for title, rating in user_ratings.items():
        movie = movies_table[movies_table['title'] == title]
        if not movie.empty:
            user_ratings_id[movie['id'].values[0]] = rating

    # Find users who rated the same movies
    seen_ids = list(user_ratings_id.keys())
    neighbours = ratings_table[ratings_table['movieId'].isin(seen_ids)]

    scores = {}
    for userId, group in neighbours.groupby('userId'):
        
        # Normalize ratings
        user_mean = group['rating'].mean()
        new_user_mean = sum(user_ratings_id[mid] for mid in group['movieId'] if mid in user_ratings_id) / len(group)
        
        # Calculate mean difference
        diff = 0
        for _, row in group.iterrows():
            if row['movieId'] in user_ratings_id:
                diff += abs((row['rating'] - user_mean) - (user_ratings_id[row['movieId']] - new_user_mean))
        diff /= len(group)
        
        similarity = 1 / (1 + diff)
        
        # Score unseen movies
        unseen = ratings_table[(ratings_table['userId'] == userId) & (~ratings_table['movieId'].isin(seen_ids))]
        for _, row in unseen.iterrows():
            mid = row['movieId']
            if mid not in scores:
                scores[mid] = {'weighted_sum': 0, 'similarity_sum': 0}
            scores[mid]['weighted_sum'] += row['rating'] * similarity
            scores[mid]['similarity_sum'] += similarity

    results = []
    for mid, val in scores.items():
        if val['similarity_sum'] < 5:  # Minimum 5 similar users
            continue
        collab_score = val['weighted_sum'] / val['similarity_sum']
        title_row = movies_table[movies_table['id'] == mid]
        if not title_row.empty:
            results.append({'id': mid, 'title': title_row['title'].values[0], 'collab_score': collab_score})
    return pd.DataFrame(results).sort_values('collab_score', ascending=False)

collab_scores = collaborative_score(user_ratings, ratings_table, movies_table)
print("\n ===COLLABORATORY SCORES===")
print(collab_scores.head(10))


#----Step 4: Hybrid scoring----------------------
'''This function combines the content-based and collaborative scores into a final score.
Both scores are normalized to a 0-1 scale before combining.
The final score is calculated as alpha * content_normalized + (1-alpha) * collab_normalized.
Alpha is set to 0.4, giving slightly more weight to the collaborative score.'''

def hybrid_score(content_scores, collab_scores, alpha=0.4):
    
    # Normalize content score
    min_c = content_scores['content_score'].min()
    max_c = content_scores['content_score'].max()
    content_scores['content_normalized'] = (content_scores['content_score'] - min_c) / (max_c - min_c)

    # Normalize collaborative score
    collab_scores['collab_normalized'] = (collab_scores['collab_score'] - 1) / 4

    # Merge both scores
    combined = content_scores.merge(collab_scores[['id', 'collab_normalized']], on='id', how='inner')

    # Final score
    combined['final_score'] = alpha * combined['content_normalized'] + (1 - alpha) * combined['collab_normalized']

    return combined[['id', 'title', 'final_score']].sort_values('final_score', ascending=False)

final_recommendations = hybrid_score(content_scores, collab_scores)
print("\n===FINAL RECOMMENDATIONS===")
print(final_recommendations.head(10))