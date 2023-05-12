import panda as pd

def read_data(user_id):
    ratings = pd.read_csv('./ratings.dat', sep='::', engine='python', names=[
        'user_id', 'movie_id', 'rating', 'timestamp'])
    movies = pd.read_csv('./movies.dat', sep='::', engine='python', names=[
        'movie_id', 'title', 'genres'], encoding='ISO-8859-1')
    # Merge the data
    data = pd.merge(ratings, movies, on='movie_id')

    # use a sample to test bc of computation time
    data = data.sample(frac=0.01, random_state=55)  # Return a random sample of items from an axis of object.
    # float value * length of data frame values,  seed for random number

    # TODO
    # Create the user-item matrix
    #user_item_matrix = pd.pivot_table(data, values='rating', index='user_id',
     #                                 columns='movie_id')
    #print('User item table', user_item_matrix)
    # TODO get user id from frontend
    # Get the user ID from the console input
    #user_id = input("Enter user ID: ")


    # Get the movies rated by the user
    user_data = data[data['user_id'] == user_id].dropna()  # select rows where column value equals id
    if len(user_data) == 0:
        print("Error: user has not rated any movies")
        exit()
    else:
        print(f"Movies rated by user {user_id}:")
        print(user_data[['title', 'genres']][:15].to_string(index=False))  # get rows 0 to max 15
