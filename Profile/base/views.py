from django.shortcuts import render
import pandas as pd
import numpy as np

# create views here

def home(request):
    return render(request, "home.html")

def projects(request):
    user_id = request.GET.get('user')
    try:
        user_id = int(user_id)
        recommended_movies = getMovies(user_id)
        print('*****************')
        print(recommended_movies.to_dict(orient="records"),)

        context = {'user_id': user_id, 'movies': recommended_movies.to_dict(orient="records"), 'movies_html': recommended_movies.to_html()}#.to_html()}

        return render(request, "projects.html", context)
    except ValueError:
        print("Error: user ID must be an integer")
        return render(request, "home.html")

def getMovies(user_id):
    ratings = pd.read_csv('./ratings.dat', sep='::', engine='python', names=[
        'user_id', 'movie_id', 'rating', 'timestamp'])
    movies = pd.read_csv('./movies.dat', sep='::', engine='python', names=[
        'movie_id', 'title', 'genres'], encoding='ISO-8859-1')
    # Merge the data
    data = pd.merge(ratings, movies, on='movie_id')

    metadata = pd.read_csv('./movies_metadata.csv')

    # use a sample to test bc of computation time
    data = data.sample(frac=0.01, random_state=55)  # Return a random sample of items from an axis of object.
    # float value * length of data frame values,  seed for random number

    # Create the user-item matrix
    user_item_matrix = pd.pivot_table(data, values='rating', index='user_id',
                                      columns='movie_id')
    #print('User item table', user_item_matrix)

    # Get the movies rated by the user
    user_data = data[data['user_id'] == user_id].dropna()  # select rows where column value equals id
    if len(user_data) == 0:
        #print("Error: user has not rated any movies")
        exit()
   # else:
        #print(f"Movies rated by user {user_id}:")
        #print(user_data[['title', 'genres']][:15].to_string(index=False))  # get rows 0 to max 15

    similarities = find_nearest_neighbor(data, user_id, user_data)

    predicted_ratings = recommend_movie(10, data, user_data, movies, similarities, user_item_matrix)  # num = 10 achieves better result than num = 5
    #print(predicted_ratings[['title', 'genres', 'predicted_rating']][:10].to_string(
     #   index=False))
    #print(predicted_ratings[['title', 'genres', 'predicted_rating']][:20])
    top_20_recommendations = predicted_ratings[:20]
    # sonst matchen titel net
    top_20_recommendations["title"] = top_20_recommendations["title"].str.replace(r"\(\d{4}\)", "").str.strip()

    print(top_20_recommendations)
    df = pd.read_csv('movies_metadata.csv', low_memory=False)
    #df.rename(columns={'id': 'movie_id'})
    print(df.columns)
   # print(top_20_recommendations.columns)
    print( df[["title", "overview", "poster_path"]])

    merged_df = pd.merge(top_20_recommendations, df[["title", "overview", "poster_path"]], on="title", how="left")


    print(merged_df)

    return merged_df

def find_nearest_neighbor(data, user_id, user_data):
    similarities = {} # dict
    for other_user_id in data['user_id']: # loop through id's
        if other_user_id != user_id:  # as we want to not look at our own stuff
            other_user_data = data[data['user_id'] == other_user_id].dropna()  # select rows where column value equals other id
            common_movies = set(user_data['movie_id']).intersection(set(
                other_user_data['movie_id']))
            if len(common_movies) > 0:
                user_ratings = user_data[user_data['movie_id'].isin(
                    common_movies)]['rating']
                other_user_ratings = other_user_data[other_user_data[
                    'movie_id'].isin(common_movies)]['rating']
                distance = np.linalg.norm(user_ratings.reset_index(drop=True) -
                                          other_user_ratings.reset_index(drop=True))
                if distance == 0:
                    similarity = 1.0
                else:
                    similarity = 1 / distance
            else:
                similarity = 0.0 # no common movies -> not a good recommendation
            similarities.update({other_user_id: similarity})
    similarities = pd.Series(data=similarities)
    similarities = similarities.sort_values(ascending=False)
    return similarities

def rating_predict(movie_id, num_neighbor, similarities, user_item_matrix):
    weighted_sum = 0.0
    weight_sum = 0.0
    for neighbor_id, similarity in similarities[:num_neighbor].iteritems(): #loop similarities
        neighbor_ratings = user_item_matrix.loc[neighbor_id][movie_id] # get matrix value
        if not np.isnan(neighbor_ratings):
            weighted_sum += similarity * neighbor_ratings
            weight_sum += similarity
    if weight_sum == 0.0:
        result = None
    else:
        result = weighted_sum / weight_sum
    return result

def recommend_movie(num_neighbor, data, user_data, movies, similarities, user_item_matrix):
    data_sample = data[data['user_id'].isin(similarities[:num_neighbor].index)] # get rows of neighbors with highest similarity
    movies_sample = movies[movies['movie_id'].isin(data_sample['movie_id'])]
    user_predicted_movie = movies_sample[~movies_sample['movie_id'].isin(user_data[
                                                                             'movie_id'])]   # tilde = inversion
                                                                                             # -> movies not in user data
    predicted_rating = user_predicted_movie['movie_id'].apply(lambda
                                                                  x:rating_predict(x,num_neighbor, similarities, user_item_matrix))
    user_predicted_movie.insert(len(user_predicted_movie.columns),
                                'predicted_rating', predicted_rating) # insert at index
    # now movie_id and predicted_rating

    return user_predicted_movie.sort_values('predicted_rating', ascending=False) # sort according to highest prediction value


def contact(request):
    return render(request, "contact.html")


