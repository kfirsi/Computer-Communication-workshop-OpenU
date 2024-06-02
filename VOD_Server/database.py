import os
import sqlite3

########################################################################################################################
#                     The following part is for creating the database and inserting the movie data.                    #
########################################################################################################################


def create_movie_database(name_of_db):
    """ Create the SQLite database and the 'movies' table. """

    # Connect to the SQLite database (create if it doesn't exist)
    db_connection = sqlite3.connect(name_of_db)
    db_cursor = db_connection.cursor()

    # Create the 'movies' table if it doesn't exist
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT,
            release_date DATE,
            length TEXT,
            genre TEXT,
            description TEXT,
            rating REAL,
            poster_image_link TEXT,
            movie_location_link TEXT
        )
    ''')
    # Commit the changes to the database.
    db_connection.commit()


def insert_movie_data(name_of_db, title, release_date, length, genre, description, rating, poster_link, movie_link):
    """ Insert the movie data into the 'movies' table. """

    # Connect to the SQLite database
    db_connection = sqlite3.connect(name_of_db)
    db_cursor = db_connection.cursor()

    # Insert the provided movie data into the 'movies' table.
    db_cursor.execute('''
        INSERT INTO movies (
            title, release_date, length, genre, description, rating, poster_image_link, movie_location_link
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, release_date, length, genre, description, rating, poster_link, movie_link))

    # Commit the changes to the database.
    db_connection.commit()


def remove_movie_data(name_of_db, movie_id):
    """ Remove the movie data from the 'movies' table. """

    # Connect to the SQLite database
    db_connection = sqlite3.connect(name_of_db)
    db_cursor = db_connection.cursor()
    # Remove the movie data from the 'movies' table.
    db_cursor.execute('''DELETE FROM movies WHERE id = ?''', (movie_id,))
    # Commit the changes to the database.
    db_connection.commit()


if __name__ == '__main__':
    # Create the database and the 'movies' table.
    db_name = 'instance/movies_database.db'
    create_movie_database(db_name)

    # Insert the provided movie data.
    insert_movie_data(
        db_name,
        'Cargo',
        '2017-05-22',
        "00:01:01",
        'Action',
        'Cargo boat carrying containers.',
        1,
        os.path.join(os.getcwd(), 'assets/Cargo.png'),
        os.path.join(os.getcwd(), 'assets/Cargo.mp4')

    )
    # Insert the provided movie data.
    insert_movie_data(
        db_name,
        'Cooking',
        '2020-04-27',
        "00:01:29",
        'Romance',
        'A chef slicing a red bell pepper with a knife.',
        4,
        os.path.join(os.getcwd(), 'assets/Cooking.png'),
        os.path.join(os.getcwd(), 'assets/Cooking.mp4')
    )

    # Insert the provided movie data.
    insert_movie_data(
        db_name,
        'Dogs',
        '2020-04-15',
        "00:00:49",
        'Adventure',
        'Dogs enjoying the snow.',
        3,
        os.path.join(os.getcwd(), 'assets/Dogs.png'),
        os.path.join(os.getcwd(), 'assets/Dogs.mp4')
    )

    # Insert the provided movie data.
    insert_movie_data(
        db_name,
        'Rickroll',
        '1987-07-27',
        "00:02:59",
        'Comedy',
        'Rickrolling is when you troll someone on the internet by linking to the music video for Rick '
        'Astley’s 1987 hit song “Never Gonna Give You Up.”',
        5,
        os.path.join(os.getcwd(), 'assets/Rickroll.png'),
        os.path.join(os.getcwd(), 'assets/Rickroll.mp4')
    )

    # Insert the provided movie data.
    insert_movie_data(
        db_name,
        'Rocket',
        '1987-07-27',
        "00:01:03",
        'Action',
        'Countdown to rocket launching.',
        4,
        os.path.join(os.getcwd(), 'assets/Rocket.png'),
        os.path.join(os.getcwd(), 'assets/Rocket.mp4')
    )

    # Insert the provided movie data.
    insert_movie_data(
        db_name,
        'Traffic',
        '2019-04-05',
        "00:01:00",
        'Thriller',
        'Traffic Flow In The Highway',
        1,
        os.path.join(os.getcwd(), 'assets/Traffic.png'),
        os.path.join(os.getcwd(), 'assets/Traffic.mp4')
    )


