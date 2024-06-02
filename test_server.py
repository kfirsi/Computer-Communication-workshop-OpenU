########################################################################################################################
#                                                        Notes:                                                        #
########################################################################################################################
#                                                                                                                      #
#   - This file contains the tests for the server side.                                                                #
#   - The client_id increases as new clients are connected to the server.                                              #
#   - The tests are run in the order they are defined (class after class, method after method).                        #
#   - To test the server parts altogether - Run this file as is, starting from the main method.                        #
#   - To test the server parts individually - Comment out the tests you don't want to run and run the file.            #
#     Make sure to adjust the client_id in the http request accordingly.                                               #
#                                                                                                                      #
########################################################################################################################


import unittest
import sqlite3
import vlc
from server import convert_movie_length_to_seconds, app, Client, Clients
from database import create_movie_database, insert_movie_data, remove_movie_data


########################################################################################################################
#                                              Testing the server routes:                                              #
########################################################################################################################


class TestConnectNewClientToServer(unittest.TestCase):
    """ Test the /connect_new_client_to_server route """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client.
        self.client = app.test_client()

    def test_connect_new_client_to_server(self):
        """ Test the /connect_new_client_to_server route """
        # Connect a new client to the server (client_id should be 1).
        response = self.client.get('/connect_new_client_to_server')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains the 'client_id' key.
        data = response.get_json()
        # Check if the response contains the 'client_id' key.
        self.assertTrue('client_id' in data)
        # Check if the client_id is a positive integer.
        client_id = data['client_id']
        self.assertTrue(isinstance(client_id, int))
        self.assertTrue(client_id > 0)
        # Exit the client.
        self.client.post('/client_exit/1')


class TestGetMovies(unittest.TestCase):
    """ Test the /get_movies route.
        Note: The Movies class is indirectly tested by the testing this route. """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client
        self.client = app.test_client()

    def test_get_movies(self):
        # Get the movies from the server.
        response = self.client.get('/get_movies')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON array of movies.
        data = response.get_json()
        self.assertTrue(isinstance(data, list))
        # If there are movies in the database, check if each movie has the expected keys.
        if data:
            for movie in data:
                self.assertTrue('id' in movie)
                self.assertTrue('name' in movie)
                self.assertTrue('poster_location' in movie)
                self.assertTrue('date' in movie)
                self.assertTrue('rating' in movie)
                self.assertTrue('genre' in movie)
                self.assertTrue('length_seconds_int' in movie)
                self.assertTrue('length_hhmmss_string' in movie)
                self.assertTrue('description' in movie)


class TestGetMovieRtpUrl(unittest.TestCase):
    """ Test the /get_movie_rtp_url route. """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client
        self.client = app.test_client()

    def test_get_movie_rtp_url(self):
        # Connect a new client to the server (client_id should be 1).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the first client.
        response = self.client.post('/get_movie_rtp_url/2/1')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON object with 'rtp_url' key.
        data = response.get_json()
        self.assertTrue('rtp_url' in data)
        # Check if the rtp_url is in the expected format.
        self.assertEqual(data['rtp_url'], 'rtsp://localhost:8554/2/1')
        # Exit the client.
        self.client.post('/client_exit/2')

    def test_get_movie_rtp_url_movie_not_found(self):
        # Connect a new client to the server (client_id should be 2).
        self.client.get('/connect_new_client_to_server')
        # Test the case where the movie doesn't exist (Assuming that the movie with id 999 doesn't exist)..
        response = self.client.post('/get_movie_rtp_url/3/999')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 405)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key.
        data = response.get_json()
        self.assertTrue('error' in data)
        # Exit the client.
        self.client.post('/client_exit/3')

    def test_get_movie_rtp_url_client_not_found(self):
        # Connect a new client to the server (client_id should be 3).
        self.client.get('/connect_new_client_to_server')
        # Test the case where the client doesn't exist (Assuming that the client with id 999 doesn't exist).
        response = self.client.post('/get_movie_rtp_url/999/1')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 404)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key.
        data = response.get_json()
        self.assertTrue('error' in data)
        # Exit the client.
        self.client.post('/client_exit/4')


class TestStartStreaming(unittest.TestCase):
    """ Test the /start_streaming route."""

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client
        self.client = app.test_client()

    def test_start_streaming(self):
        """ Test the /start_streaming route. """
        # Connect a new client to the server (client_id should be 1).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the first client.
        self.client.post('/get_movie_rtp_url/5/1')
        # Start streaming for the client.
        response = self.client.post('/start_streaming/5')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON object with 'message' key.
        data = response.get_json()
        self.assertTrue('message' in data)
        # Exit the client.
        self.client.post('/client_exit/5')

    def test_start_streaming_client_already_streaming_a_movie(self):
        # Connect a new client to the server (client_id should be 6).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the second client.
        self.client.post('/get_movie_rtp_url/6/1')
        # Start streaming for the client.
        self.client.post('/start_streaming/6')
        # Try to start streaming for the client that is already streaming.
        response = self.client.post('/start_streaming/6')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 400)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key.
        data = response.get_json()
        self.assertTrue('error' in data)
        # Stop streaming for the client.
        self.client.post('/stop_streaming/6')
        # Exit the client.
        self.client.post('/client_exit/6')

    def test_start_streaming_client_not_found(self):
        # Connect a new client to the server (client_id should be 2).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the second client.
        self.client.post('/get_movie_rtp_url/7/1')
        # Try to start streaming for a non-existent client (Assuming that the client with id 999 doesn't exist).
        response = self.client.post('/start_streaming/999')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 404)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key.
        data = response.get_json()
        self.assertTrue('error' in data)
        # Exit the client.
        self.client.post('/client_exit/7')


class TestSkipToTimestamp(unittest.TestCase):
    """ Test the /skip_to_timestamp route. """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client
        self.client = app.test_client()

    def test_skip_to_timestamp(self):
        """ Test the /skip_to_timestamp route. """
        # Connect a new client to the server (client_id should be 1).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the first client.
        self.client.post('/get_movie_rtp_url/8/1')
        # Start streaming for the client.
        self.client.post('/start_streaming/8')
        # Skip to a specific timestamp for the client.
        response = self.client.post('/skip_to_timestamp/8/01:23:45')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON object with 'message' key.
        data = response.get_json()
        self.assertTrue('message' in data)
        # Stop streaming for the client.
        self.client.post('/stop_streaming/8')
        # Exit the client.
        self.client.post('/client_exit/8')

    def test_skip_to_timestamp_client_not_found(self):
        # Connect a new client to the server (client_id should be 2).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the second client.
        self.client.post('/get_movie_rtp_url/9/1')
        # Start streaming for the client.
        self.client.post('/start_streaming/9')
        # Skip to a specific timestamp for a non-existent client (Assuming that the client with id 999 doesn't exist).
        response = self.client.post('/skip_to_timestamp/999/01:23:45')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 404)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key.
        data = response.get_json()
        self.assertTrue('error' in data)
        # Stop streaming for the client.
        self.client.post('/stop_streaming/9')
        # Exit the client.
        self.client.post('/client_exit/9')

    def test_skip_to_timestamp_client_not_streaming(self):
        # Connect a new client to the server (client_id should be 3).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the third client.
        self.client.post('/get_movie_rtp_url/10/1')
        # Try to skip to a specific timestamp for a client that is not streaming.
        response = self.client.post('/skip_to_timestamp/10/01:23:45')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 400)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key.
        data = response.get_json()
        self.assertTrue('error' in data)
        # Exit the client.
        self.client.post('/client_exit/10')


class TestStopStreamRoute(unittest.TestCase):
    """ Test the /stop_streaming route. """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client to simulate requests
        self.client = app.test_client()

    def test_stop_stream_success(self):
        # Connect a new client to the server (client_id should be 1).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the first client.
        self.client.post('/get_movie_rtp_url/11/1')
        # Start streaming for the client.
        self.client.post('/start_streaming/11')
        # Stop streaming for the client.
        response = self.client.get('/stop_streaming/11/1')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON object with 'message' key.
        data = response.get_json()
        self.assertTrue('message' in data)
        # Exit the client.
        self.client.post('/client_exit/11')

    def test_stop_stream_not_streaming(self):
        # Connect a new client to the server (client_id should be 3).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the third client.
        self.client.post('/get_movie_rtp_url/12/1')
        # Stop streaming for the client that is not streaming.
        response = self.client.get('/stop_streaming/12/1')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 400)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key
        data = response.get_json()
        self.assertTrue('error' in data)
        # Exit the client.
        self.client.post('/client_exit/12')

    def test_stop_stream_client_not_found(self):
        # Connect a new client to the server (client_id should be 2).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the second client.
        self.client.post('/get_movie_rtp_url/13/1')
        # Start streaming for the client.
        self.client.post('/start_streaming/13')
        # Try to stop streaming for a non-existent client (Assuming that the client with id 999 doesn't exist).
        response = self.client.get('/stop_streaming/999/1')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 404)
        # Check if the response content type is 'application/json'.
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key
        data = response.get_json()
        self.assertTrue('error' in data)
        # Stop streaming for the client.
        self.client.post('/stop_streaming/13')
        # Exit the client.
        self.client.post('/client_exit/13')


class TestDownloadProjectPortfolio(unittest.TestCase):
    """ Test the /download_project_portfolio route. """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client
        self.client = app.test_client()

    def test_download_project_portfolio(self):
        """ Test the /download_project_portfolio route. """
        # Download the project portfolio.
        response = self.client.get('/download_project_portfolio')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is set to
        # 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        self.assertEqual(
            response.content_type,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        # Check if the response contains the expected download header
        self.assertTrue('Content-Disposition' in response.headers)
        self.assertTrue('attachment' in response.headers['Content-Disposition'])
        self.assertTrue('project_portfolio.docx' in response.headers['Content-Disposition'])


class TestHandleClientExit(unittest.TestCase):
    """ Test the /client_exit route. """

    def setUp(self):
        """ Create a test client to simulate requests to the server. """
        # Create a test client
        self.client = app.test_client()

    def test_handle_client_exit_client_not_streaming(self):
        # Connect a new client to the server (client_id should be 1).
        self.client.get('/connect_new_client_to_server')
        # Exit the client.
        response = self.client.post('/client_exit/14')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 200)
        # Check if the response content type is 'application/json'
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON object with 'message' key
        data = response.get_json()
        self.assertTrue('message' in data)

    def test_handle_client_exit_client_streaming(self):
        # Connect a new client to the server (client_id should be 2).
        self.client.get('/connect_new_client_to_server')
        # Get the RTP URL for the first movie for the first client.
        self.client.post('/get_movie_rtp_url/15/1')
        # Start streaming for the client.
        self.client.post('/start_streaming/15')
        # Exit the client.
        response = self.client.post('/client_exit/15')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 201)
        # Check if the response content type is 'application/json'
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains a JSON object with 'message' key
        data = response.get_json()
        self.assertTrue('message' in data)

    def test_handle_client_exit_client_not_found(self):
        # Connect a new client to the server (client_id should be 3).
        self.client.get('/connect_new_client_to_server')
        # Try to handle exit for a non-existent client (Assuming that the client with id 999 doesn't exist).
        response = self.client.post('/client_exit/999')
        # Assert that the response is as expected.
        self.assertEqual(response.status_code, 404)
        # Check if the response content type is 'application/json'
        self.assertEqual(response.content_type, 'application/json')
        # Check if the response contains an 'error' key
        data = response.get_json()
        self.assertTrue('error' in data)
        # Exit the client.
        self.client.post('/client_exit/16')


########################################################################################################################
#                                               Testing utility methods:                                               #
########################################################################################################################


class TestMovieLengthConversion(unittest.TestCase):

    def test_conversion(self):
        # Test with a sample movie length
        movie_length = "02:30:45"
        expected_seconds = 2 * 3600 + 30 * 60 + 45
        self.assertEqual(convert_movie_length_to_seconds(movie_length), expected_seconds)

    def test_zero_length(self):
        # Test with a movie length of 0
        movie_length = "00:00:00"
        expected_seconds = 0
        self.assertEqual(convert_movie_length_to_seconds(movie_length), expected_seconds)

    def test_hours_only(self):
        # Test with a movie length in hours only
        movie_length = "03:00:00"
        expected_seconds = 3 * 3600
        self.assertEqual(convert_movie_length_to_seconds(movie_length), expected_seconds)

    def test_minutes_only(self):
        # Test with a movie length in minutes only
        movie_length = "00:45:00"
        expected_seconds = 45 * 60
        self.assertEqual(convert_movie_length_to_seconds(movie_length), expected_seconds)

    def test_seconds_only(self):
        # Test with a movie length in seconds only
        movie_length = "00:00:30"
        expected_seconds = 30
        self.assertEqual(convert_movie_length_to_seconds(movie_length), expected_seconds)


########################################################################################################################
#                                       Testing the Client and clients classes:                                        #
########################################################################################################################


class TestClient(unittest.TestCase):
    """ Test the Client class. """

    def test_client_initialization(self):
        """ Test the Client class initialization. """
        # Create a Client instance.
        client = Client(client_id=1)
        # Check if client_id is set correctly during initialization.
        self.assertEqual(client.get_id(), 1)
        # Check if other attributes are initialized correctly.
        self.assertIsInstance(client.get_instance(), vlc.Instance)
        # Check if the player is an instance of vlc.MediaPlayer.
        self.assertIsNone(client.get_player())
        # Check if the media is None.
        self.assertIsNone(client.get_media())
        # Check if the options is an empty string.
        self.assertEqual(client.get_options(), '')
        # Check if is_streaming is False.
        self.assertFalse(client.get_is_streaming())

    def test_setters_and_getters(self):
        """ Test the Client class setters and getters. """
        # Create a Client instance.
        client = Client(client_id=1)
        # Set new values for the attributes.
        new_instance = vlc.Instance('--no-xlib')
        # Create a new player.
        new_player = new_instance.media_player_new()
        # Create a new media.
        new_media = new_instance.media_new("C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.mkv")
        # Set new options.
        new_options = '--fullscreen'
        # Set is_streaming to True.
        new_is_streaming = True

        # Set the client id.
        client.set_id(2)
        # Set the client instance.
        client.set_instance(new_instance)
        # Set the client player.
        client.set_player(new_player)
        # Set the client media.
        client.set_media(new_media)
        # Set the client options.
        client.set_options(new_options)
        # Set the client is_streaming.
        client.set_is_streaming(new_is_streaming)

        # Check if the id is updated correctly.
        self.assertEqual(client.get_id(), 2)
        # Check if the instance is updated correctly.
        self.assertEqual(client.get_instance(), new_instance)
        # Check if the player is updated correctly.
        self.assertEqual(client.get_player(), new_player)
        # Check if the media is updated correctly.
        self.assertEqual(client.get_media(), new_media)
        # Check if the options is updated correctly.
        self.assertEqual(client.get_options(), new_options)
        # Check if is_streaming is updated correctly.
        self.assertTrue(client.get_is_streaming())


class TestClients(unittest.TestCase):
    """ Test the Clients class. """

    def setUp(self):
        """ Create a Clients instance to test. """
        # Create a Clients instance.
        self.clients = Clients()

    def test_clients_initialization(self):
        """ Test the Clients class initialization. """
        # Check if the clients dictionary is empty during initialization.
        self.assertEqual(self.clients.get_number_of_connected_clients(), 0)
        # Check if the number of streaming clients is 0 during initialization.
        self.assertEqual(self.clients.get_number_of_streaming_clients(), 0)
        # Check if the client_id_counter is 0 during initialization.
        self.assertEqual(self.clients.get_client_id_counter(), 0)
        # Check if the clients dictionary is empty during initialization.
        self.assertEqual(len(self.clients.get_clients()), 0)

    def test_add_remove_client(self):
        """ Test the add_client and remove_client methods. """
        # Add a new client.
        self.clients.add_client()
        # Check if the number of connected clients is updated correctly.
        self.assertEqual(self.clients.get_number_of_connected_clients(), 1)
        # Check if the client dictionary is updated correctly.
        self.assertEqual(len(self.clients.get_clients()), 1)
        # Get the client_id of the first client added.
        client_id = list(self.clients.get_clients().keys())[0]
        # Remove the client.
        self.clients.remove_client(client_id)
        # Check if the number of connected clients is updated correctly after removal.
        self.assertEqual(self.clients.get_number_of_connected_clients(), 0)
        # Check if the client is removed from the dictionary.
        self.assertEqual(len(self.clients.get_clients()), 0)

    def test_get_client(self):
        """ Test the get_client method. """
        # Add a new client.
        self.clients.add_client()
        # Get the client_id of the first client added.
        client_id = self.clients.get_client_id_counter()
        # Get the first client added.
        client = self.clients.get_client(client_id)
        # Check if the client is an instance of Client.
        self.assertIsInstance(client, Client)
        # Check if the client_id is the same.
        self.assertEqual(client.get_id(), client_id)
        # Try to get a non-existent client (Assuming that the client with id 999 doesn't exist).
        non_existent_client = self.clients.get_client(999)
        # Check if None is returned for non-existent client.
        self.assertIsNone(non_existent_client)

    def test_reset_clients(self):
        """ Test the reset_clients method. """
        # Add a new client.
        self.clients.add_client()
        # Get the client_id of the first client added.
        client_id = list(self.clients.get_clients().keys())[0]
        # Reset the client.
        self.clients.reset_client(client_id)
        # Check if the client is reset to a new instance.
        client = self.clients.get_client(client_id)
        # Check if the client is an instance of Client.
        self.assertIsInstance(client, Client)
        # Check if the client_id is the same.
        self.assertIsInstance(client.get_instance(), vlc.Instance)


########################################################################################################################
#                                                Testing the database:                                                 #
########################################################################################################################


class TestDatabase(unittest.TestCase):
    """ Test the database.py functions. """

    def setUp(self):
        """ Create a test database. """
        # Set the database name.
        self.DB_NAME = 'test_movies_database.db'

    def test_create_movie_database(self):
        """ Test the create_movie_database function. """
        # Create a test database.
        create_movie_database(self.DB_NAME)
        # Create a connection to the test database.
        self.connection = sqlite3.connect(self.DB_NAME)
        # Create a cursor to execute SQL queries.
        self.cursor = self.connection.cursor()
        # Verify that the 'movies' table exists.
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies';")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "The 'movies' table should exist in the database.")
        # Close the connection to the database.
        self.connection.close()

    def test_insert_movie_data(self):
        """ Test the insert_movie_data function. """
        # Create a connection to the test database.
        self.connection = sqlite3.connect(self.DB_NAME)
        # Create a cursor to execute SQL queries.
        self.cursor = self.connection.cursor()
        # Insert movie data.
        insert_movie_data(
            self.DB_NAME,
            'Test Movie',
            '2023-11-01',
            '01:30:00',
            'Test Genre',
            'Test Description',
            4,
            'test_poster.png',
            'test_movie.mkv'
        )
        # Verify that the inserted data exists in the database.
        self.cursor.execute("SELECT title FROM movies WHERE title='Test Movie';")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "The inserted movie data should exist in the database.")
        # Close the connection to the database.
        self.connection.close()

    def test_remove_movie_data(self):
        """ Test the remove_movie_data function. """
        # Create a connection to the test database.
        self.connection = sqlite3.connect(self.DB_NAME)
        # Create a cursor to execute SQL queries.
        self.cursor = self.connection.cursor()
        # Remove the inserted movie data.
        remove_movie_data(self.DB_NAME, 1)
        # Verify that the inserted data doesn't exist in the database.
        self.cursor.execute("SELECT title FROM movies WHERE title='Test Movie';")
        result = self.cursor.fetchone()
        self.assertIsNone(result, "The removed movie data should not exist in the database.")
        # Close the connection to the database.
        self.connection.close()


if __name__ == '__main__':
    unittest.main()
