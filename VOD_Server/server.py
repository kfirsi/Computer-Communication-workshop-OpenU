########################################################################################################################
#                                                        Notes:                                                        #
########################################################################################################################
#                                                                                                                      #
#   - This file contains the server side of the VOD application.                                                       #
#     It is a GUI application that allows the user to browse a list of movies and watch them.                          #
#   - This file contains the following classes:                                                                        #
#     - Movies:                                                                                                        #
#       This class represents the Movies table in the database.                                                         #
#       This class inherits from the db.Model class which declares the class as a model for the database.              #
#     - Client:                                                                                                        #
#       This class represents a client connected to the server.                                                         #
#       Each client has a unique ID and a VLC media player instance.                                                   #
#       The media player instance is used to play the movie for the client.                                            #
#     - Clients:                                                                                                       #
#       This class represents a collection of clients connected to the server.                                         #
#       Each client has a unique ID and a VLC media player instance.                                                   #
#       The media player instance is used to play the movie for the client.                                            #
#                                                                                                                      #
########################################################################################################################

from flask import Flask, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
import vlc

########################################################################################################################
#                     The following part is used to handle the flask application and the database.                     #
########################################################################################################################

# Create the Flask app
app = Flask(__name__)

# Configure the SQLite database URI to point to your existing database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies_database.db'
db = SQLAlchemy(app)


class Movies(db.Model):
    """ This class represents the Movies table in the database.
        This class inherits from the db.Model class which declares the class as a model for the database.
    Attributes:

        id:
            (int) The ID of the movie.

        title:
            (str) The title of the movie.

        release_date:
            (Date) The release date of the movie.

        length:
            (int) The length of the movie in HH:MM:SS format.

        genre:
            (int) The genre of the movie.

        description:
            (int) The description of the movie.

        rating:
            (str) The rating of the movie.

        poster_image_link:
            (int) The link to the poster image of the movie.

        movie_location_link:
            (int) The link to the movie location.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    length = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    description = db.Column(db.String(255))
    rating = db.Column(db.Integer)
    poster_image_link = db.Column(db.String(255))
    movie_location_link = db.Column(db.String(255))

    def as_dict(self):
        """ This method returns the movie as a dictionary. """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


########################################################################################################################
#                                    The following part is used to handle the clients.                                 #
########################################################################################################################


class Client:
    """ This class represents a client connected to the server.
    Each client has a unique ID and a VLC media player instance.
    The media player instance is used to play the movie for the client.
    Attributes:
        id:
            (int) The ID of the client.
        instance:
            (vlc.Instance) The VLC media player instance.
        player:
            (vlc.MediaPlayer) The VLC media player.
        media:
            (vlc.Media) The VLC media.
        options:
            (str) The VLC media player options.
        is_streaming:
            (bool) A flag indicating whether the client is currently streaming a movie or not.
    """

    def __init__(self, client_id=None):
        """ Initialize the client with the specified ID and a new VLC media player instance. """
        self.id = client_id
        self.instance = vlc.Instance('--no-xlib')  # '--no-xlib' means no GUI (only CLI)
        self.player = None
        self.media = None
        self.options = ''
        self.is_streaming = False

    def set_id(self, client_id):
        """ Set the ID of the client.
        Parameters:
            client_id:
                (int) The ID of the client.
        """
        self.id = client_id

    def set_instance(self, instance):
        """ Set the VLC media player instance.
        Parameters:
            instance:
                (vlc.Instance) The VLC media player instance.
        """
        self.instance = instance

    def set_player(self, player):
        """ Set the VLC media player.
        Parameters:
            player:
                (vlc.MediaPlayer) The VLC media player.
        """
        self.player = player

    def set_media(self, media):
        """ Set the VLC media.
        Parameters:
            media:
                (vlc.Media) The VLC media.
        """
        self.media = media

    def set_options(self, options):
        """ Set the VLC media player options.
        Parameters:
            options:
                (str) The VLC media player options.
        """
        self.options = options

    def set_is_streaming(self, is_streaming):
        """ Set the is_streaming flag.
        Parameters:
            is_streaming:
                (bool) The is_streaming flag.
        """
        self.is_streaming = is_streaming

    def get_id(self):
        """ Get the ID of the client.
        Returns:
            The ID of the client.
        """
        return self.id

    def get_instance(self):
        """ Get the VLC media player instance.
        Returns:
            The VLC media player instance.
        """
        return self.instance

    def get_player(self):
        """ Get the VLC media player.
        Returns:
            The VLC media player.
        """
        return self.player

    def get_media(self):
        """ Get the VLC media.
        Returns:
            The VLC media.
        """
        return self.media

    def get_options(self):
        """ Get the VLC media player options.
        Returns:
            The VLC media player options.
        """
        return self.options

    def get_is_streaming(self):
        """ Get the is_streaming flag.
        Returns:
            The is_streaming flag.
        """
        return self.is_streaming


class Clients:
    """ This class represents a collection of clients connected to the server.
    Each client has a unique ID and a VLC media player instance.
    The media player instance is used to play the movie for the client.
    Attributes:
        clients:
            (dict) A dictionary containing all the clients.
        connected_clients:
            (int) The number of connected clients.
        streaming_clients:
            (int) The number of streaming clients.
        client_id_counter:
            (int) The client ID counter.
    """

    def __init__(self):
        """ Initialize the clients dictionary and the connected clients counter.  """
        self.clients = {}
        self.connected_clients = 0
        self.streaming_clients = 0
        self.client_id_counter = 0

    def add_client(self):
        """ Add a new client to the clients dictionary. """
        self.connected_clients += 1
        self.client_id_counter += 1
        self.clients[self.client_id_counter] = Client(self.client_id_counter)

    def remove_client(self, client_id):
        """ Remove a client from the clients dictionary.
        Parameters:
            client_id:
                (int) The ID of the client.
        """
        del self.clients[client_id]
        self.connected_clients -= 1

    def get_client(self, client_id):
        """ Get a client from the clients dictionary.
        Parameters:
            client_id:
                (int) The ID of the client.
        Returns:
            The client with the specified ID.
        """
        if client_id not in self.clients:
            return None
        return self.clients[client_id]

    def reset_client(self, client_id):
        """ Reset a client in the clients dictionary.
        Parameters:
            client_id:
                (int) The ID of the client.
        """
        self.clients[client_id] = Client(client_id)

    def get_clients(self):
        """ Get all the clients from the clients dictionary.
        Returns:
            A list of all the clients.
        """
        return self.clients

    def get_number_of_connected_clients(self):
        """ Get the number of connected clients.
        Returns:
            The number of connected clients.
        """
        return self.connected_clients

    def get_number_of_streaming_clients(self):
        """ Get the number of streaming clients.
        Returns:
            The number of streaming clients.
        """
        return self.streaming_clients

    def get_client_id_counter(self):
        """ Get the client ID counter.
        Returns:
            The client ID counter.
        """
        return self.client_id_counter

    def increase_streaming_clients_counter(self):
        """ Increase the number of streaming clients by 1. """
        self.streaming_clients += 1

    def decrease_streaming_clients_counter(self):
        """ Decrease the number of streaming clients by 1. """
        self.streaming_clients -= 1

    def decrease_connected_clients_counter(self):
        """ Decrease the number of connected clients by 1. """
        self.connected_clients -= 1


# Create a new clients object to store all the clients.
clients = Clients()


########################################################################################################################
#                                     The following part is used to handle the routes.                                 #
########################################################################################################################


@app.route('/connect_new_client_to_server', methods=['GET'])
def connect_new_client_to_server():
    """ This route is used to connect a new client to the server.
    Returns:
        A JSON object containing the client ID.
    """
    # Add a new client to the clients dictionary.
    clients.add_client()
    # Get the clients dictionary.
    clients.get_clients()
    # Return the client ID generated by the server.
    return jsonify({'client_id': clients.get_client_id_counter()}), 200


@app.route('/get_movies', methods=['GET'])
def get_movies():
    """ This route is used to get a list of movies from the database.
    Returns:
        A JSON object containing a list of movies.
    """
    # Query the database to get a list of movies.
    movies_in_database = Movies.query.all()
    # Create a list of movies.
    movie_list = [
        {
            'id': movie.id,
            'name': movie.title,
            'poster_location': movie.poster_image_link,
            'date': movie.release_date.strftime('%d/%m/%Y'),
            'rating': movie.rating,
            'genre': movie.genre,
            'length_seconds_int': convert_movie_length_to_seconds(movie.length),
            'length_hhmmss_string': movie.length,
            'description': movie.description,
        } for movie in movies_in_database]
    clients.get_clients()

    return jsonify(movie_list), 200


@app.route('/get_movie_rtp_url/<int:client_id>/<int:movie_id>', methods=['POST'])
def get_movie_rtp_url(client_id, movie_id):
    """ This route is used to get the RTSP stream URL for a specific movie.

    Parameters:

        client_id:
            (int) The ID of the client.

        movie_id:
            (int) The ID of the movie.

    Returns:
        A JSON object containing a success message.
    """

    # Create a new session to query the database.
    session = sessionmaker(bind=db.engine)()

    # Query the database to get the movie with the specified ID.
    movie = session.get(Movies, movie_id)

    # Check if the movie exists.
    if movie:
        # Get the client with the specified ID.
        client = clients.get_client(client_id)
        # Check if the client exists.
        if client is None:
            return jsonify({'error': 'Client not found'}), 404
        # Check if the client is already streaming a movie
        if client.player is None:
            # Create a new VLC media player instance
            client.player = client.instance.media_player_new()
        # Create a new VLC media instance
        client.media = client.instance.media_new(movie.movie_location_link)
        # Add the VLC media player options
        client.media.add_option(f':sout=#rtp{{sdp=rtsp://:8554/{client_id}/{movie_id}}}')

        # Set the VLC media to the VLC media player
        client.player.set_media(client.media)

        # Get the RTSP stream URL
        rtp_url = f'rtsp://localhost:8554/{client_id}/{movie_id}'  # Replace 'localhost' with the actual
        # return the RTP stream URL
        return jsonify({'rtp_url': rtp_url}), 200
    # Return an error message
    return jsonify({'error': 'Movie not found'}), 405


@app.route('/start_streaming/<int:client_id>', methods=['POST'])
def start_streaming(client_id):
    """ This route is used to start streaming a movie for a specific client.

    Parameters:
        client_id:
            (int) The ID of the client.

    Returns:
        A JSON object containing a success message.
    """
    # Get the client with the specified ID.
    client = clients.get_client(client_id)
    # Check if the client exists.
    if client is None:
        return jsonify({'error': 'Client not found'}), 404
    # Check if the client is currently not streaming a movie
    if not client.is_streaming:
        # Set the is_streaming flag to True
        client.is_streaming = True
        # Increase the number of streaming clients by 1
        clients.increase_streaming_clients_counter()
        # Play the media file
        client.player.play()
        # Return a message indicating that the movie has started streaming
        return jsonify({'message': f'Successfully started streaming for client {client_id}'}), 200
    else:
        # Return an error message
        return jsonify({'error': 'Client is already streaming a movie'}), 400


# Route to handle skipping to a specific timestamp
@app.route('/skip_to_timestamp/<int:client_id>/<string:hours>:<string:minutes>:<string:seconds>', methods=['POST'])
def skip_to_timestamp(client_id, hours, minutes, seconds):
    """ This route is used to skip to a specific timestamp for a specific client.

    Parameters:

        client_id:
            (int) The ID of the client.

        hours:
            (str) The hours of the timestamp.

        minutes:
            (str) The minutes of the timestamp.

        seconds:
            (str) The seconds of the timestamp.

    Returns:
        A JSON object containing a success message.
    """
    # Get the client with the specified ID.
    client = clients.get_client(client_id)
    # Check if the client exists.
    if client is None:
        return jsonify({'error': 'Client not found'}), 404
    # Check if the client is currently streaming a movie
    if client.media and client.player and client.is_streaming:
        # Convert the timestamp to milliseconds (VLC uses milliseconds)
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        seek_time_ms = total_seconds * 1000
        # Get the timestamp in HH:MM:SS format
        timestamp = f'{hours}:{minutes}:{seconds}'
        # Set the time position to the specified timestamp
        client.player.set_time(seek_time_ms)
        # Start playing from the specified timestamp
        client.player.play()
        # Return a message indicating that the movie has skipped to the specified timestamp
        return jsonify({'message': f'Successfully skipped to {timestamp} for client {client_id}'}), 200
    else:
        # Return an error message
        return jsonify({'error': 'Client is not currently streaming any movie'}), 400


@app.route('/stop_streaming/<int:client_id>/<int:movie_id>', methods=['GET'])
def stop_stream(client_id, movie_id):
    """ This route is used to stop streaming a movie for a specific client.

    Parameters:

        client_id:
            (int) The ID of the client.

        movie_id:
            (int) The ID of the movie.

    Returns:
        A JSON object containing a success message.
    """
    # Get the client with the specified ID.
    client = clients.get_client(client_id)
    # Check if the client exists.
    if client is None:
        return jsonify({'error': 'Client not found'}), 404
    # Check if the client is currently streaming a movie
    if client.is_streaming:
        # Stop the VLC media player for the specified movie
        client.player.stop()
        # Set the is_streaming flag to False
        client.is_streaming = False
        # Reset the client
        clients.reset_client(client_id)
        # Decrease the number of streaming clients by 1
        clients.decrease_streaming_clients_counter()
        # Return a message indicating that the movie has stopped streaming
        return jsonify({'message': f'Stopped streaming movie {movie_id} for client {client_id}'}), 200
    else:
        # Return an error message
        return jsonify({'error': 'Client is not currently streaming any movie'}), 400


@app.route('/download_project_portfolio', methods=['GET'])
def download_project_portfolio():
    """ This route is used to download the project portfolio file.
    Returns:
        project portfolio file.
    """
    # Send the project portfolio file
    response = send_file(
        "./assets/project_portfolio.docx",
        as_attachment=True,
        download_name='project_portfolio.docx'
    )
    return response


@app.route('/client_exit/<int:client_id>', methods=['POST'])
def handle_client_exit(client_id):
    """ This route is used to handle a client exiting the application.

    Parameters:
        client_id:
            (int) The ID of the client.

    Returns:
        A JSON object containing a success message.
    """
    # Get the client with the specified ID.
    client = clients.get_client(client_id)
    # Check if the client exists.
    if client is None:
        # Return an error message
        return jsonify({'error': 'Client not found'}), 404

    # Check if the client is currently streaming a movie
    if client.is_streaming:
        # Stop the VLC media player for the specified movie
        client.player.stop()
        # Set the is_streaming flag to False
        client.is_streaming = False
        # Reset the client
        clients.remove_client(client_id)
        # Decrease the number of connected clients by 1
        clients.decrease_streaming_clients_counter()
        # Return a message indicating that the client has exited unexpectedly
        return jsonify({'message': f'Client {client_id} has exited unexpectedly and stopped the movie streaming.'}), 201
    else:
        # Remove the client from the clients dictionary
        clients.remove_client(client_id)
        # Return a message indicating that the client has exited
        return jsonify({'message': f'Client {client_id} has exited'}), 200


########################################################################################################################
#                                     The following part is used to handle the utilities.                              #
########################################################################################################################

def convert_movie_length_to_seconds(movie_length_in_hhmmss):
    """ This method converts a movie length from HH:MM:SS format to seconds.
    Parameter:
        movie_length_in_hhmmss:
            (str) The movie length in HH:MM:SS format.
    Returns:
        The movie length in seconds.
    """
    # Split the movie length string into hours, minutes and seconds.
    hours, minutes, seconds = movie_length_in_hhmmss.split(':')
    # Return the movie length in seconds.
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


########################################################################################################################
#                                     The following part is used to handle the main function.                          #
########################################################################################################################


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
