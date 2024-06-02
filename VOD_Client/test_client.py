########################################################################################################################
#                                                        Notes:                                                        #
########################################################################################################################
#                                                                                                                      #
#   - This file contains the tests for the client side.                                                                #
#   - The tests are run in the order they are defined (class after class, method after method).                        #
#   - To test the server parts altogether - Run this file as is, starting from the main method.                        #
#   - To test the server parts individually - Comment out the tests you don't want to run and run the file.            #
#     Make sure to adjust the client_id in the http request accordingly.                                               #
#                                                                                                                      #
########################################################################################################################


import unittest
import io
import tkinter as tk
from unittest.mock import patch, Mock
from client import Client, MovieGalleryWindow, main_window_to_export, root, SelectedMovieWindow, MoviePlayerWindow

########################################################################################################################
#                                       Testing the Client-Server communication:                                       #
########################################################################################################################


class TestClient(unittest.TestCase):
    """ Test the Client class. """

    @patch('client.requests.get')
    def test_connect_client_to_server(self, mock_get):
        """ Test the connect_client_to_server method of the Client class. """
        # Create an instance of Client class.
        my_client = Client()

        # Mock the server response.
        mock_response = Mock()
        mock_response.json.return_value = {'client_id': 123}
        mock_get.return_value = mock_response

        # Connect the client to the server.
        my_client.connect_client_to_server()

        # Assert that the client_id attribute is set to the expected value.
        self.assertEqual(my_client.client_id, mock_get.return_value.json.return_value['client_id'])

    @patch('client.requests.get')
    def test_get_movies_from_server_success(self, mock_get):
        """ Test the get_movies_from_server method of the Client class,
        when the server returns a successful response. """

        # Create an instance of Client class.
        my_client = Client()

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'id': 1,
            'name': 'Movie 1',
            'poster_location': '/path/to/poster',
            'date': '01/01/2023',
            'rating': 5,
            'genre': 'Action',
            'length_seconds_int': 3600,
            'length_hhmmss_string': '01:00:00',
            'description': 'Action-packed movie'
        }]
        mock_get.return_value = mock_response

        # Get movies from the server.
        my_client.get_movies_from_server()

        # Assert that the movies attribute is set to the expected value.
        expected_movies = [{
            'id': 1,
            'name': 'Movie 1',
            'poster_location': '/path/to/poster',
            'date': '01/01/2023',
            'rating': 5,
            'genre': 'Action',
            'length_seconds_int': 3600,
            'length_hhmmss_string': '01:00:00',
            'description': 'Action-packed movie'
        }]
        # Assert that the movies attribute is set to the expected value.
        self.assertEqual(my_client.movies, expected_movies)

    @patch('client.requests.get')
    def test_get_movies_from_server_failure(self, mock_get):
        """ Test the get_movies_from_server method of the Client class,
        when the server returns a failed response. """

        # Create an instance of Client class.
        my_client = Client()

        # Mock the server response for a failed request.
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Failed to get movies'}
        mock_get.return_value = mock_response

        # Redirect console output to a StringIO object for error message capture.
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Call the method to get movies from the server
            my_client.get_movies_from_server()

            # Assert that the error message is printed to the console.
            self.assertEqual(mock_stdout.getvalue().strip(), 'Error: Failed to get movies')

    @patch('client.requests.post')
    def test_get_movie_rtp_url_success(self, mock_post):
        """ Test the get_movie_rtp_url method of the Client class,
        when the server returns a successful response. """

        # Create an instance of Client class.
        my_client = Client()

        # Set client_id and selected_movie_id to valid values.
        my_client.client_id = 1

        # Set client_id and selected_movie_id to valid values.
        my_client.set_selected_movie_id(123)

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'rtp_url': 'rtsp://localhost:8554/1/123'}
        mock_post.return_value = mock_response

        # Get the RTP URL of the movie.
        rtp_url = my_client.get_movie_rtp_url()

        # Assert that the rtp_url attribute is set to the expected value.
        expected_rtp_url = 'rtsp://localhost:8554/1/123'
        self.assertEqual(my_client.rtp_url, expected_rtp_url)

        # Check if the method returns the expected RTP URL
        self.assertEqual(rtp_url, expected_rtp_url)

    @patch('client.requests.post')
    def test_get_movie_rtp_url_failure(self, mock_post):
        """ Test the get_movie_rtp_url method of the Client class,
        when the server returns a failed response. """

        # Create an instance of Client class.
        my_client = Client()

        # Set client_id to valid values.
        my_client.client_id = 1

        # Set selected_movie_id to valid values.
        my_client.set_selected_movie_id(123)

        # Mock the server response for a failed request.
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Failed to get RTP URL'}
        mock_post.return_value = mock_response

        # Redirect console output to a StringIO object for error message capture.
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Get the RTP URL of the movie.
            rtp_url = my_client.get_movie_rtp_url()

            # Assert that the error message is printed to the console.
            self.assertEqual(mock_stdout.getvalue().strip(), 'Error: Failed to get RTP URL')

    @patch('client.requests')
    def test_start_streaming_movie_success(self, mock_requests):
        """ Test the start_streaming_movie method of the Client class,
        when the server returns a successful response."""

        # Simulate a successful request.
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.json.return_value = {'message': 'Streaming started successfully'}

        # Create an instance of Client class.
        my_client = Client()

        # Set the client ID.
        my_client.client_id = 123

        # Call the method and check if it logs the success message.
        with self.assertLogs(my_client.logger, level='INFO'):
            # Start streaming the movie.
            my_client.start_streaming_movie()

    @patch('client.requests')
    def test_start_streaming_movie_failure(self, mock_requests):
        """ Test the start_streaming_movie method of the Client class,
        when the server returns a failed response."""

        # Simulate a failed request.
        mock_requests.post.return_value.status_code = 404
        mock_requests.post.return_value.json.return_value = {'error': 'Failed to start streaming'}

        # Create an instance of Client class.
        my_client = Client()

        # Set the client ID.
        my_client.client_id = 456

        # Call the method and check if it logs the error message.
        with self.assertLogs(my_client.logger, level='ERROR'):
            # Start streaming the movie.
            my_client.start_streaming_movie()

    @patch('client.requests')
    def test_skip_to_timestamp_success(self, mock_requests):
        """ Test the skip_to_timestamp method of the Client class,
        when the server returns a successful response."""

        # Simulate a successful request.
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.json.return_value = {'message': 'Skipped to timestamp successfully'}

        # Create an instance of Client class.
        my_client = Client()

        # Set the client ID.
        my_client.client_id = 123

        # Call the method and check if it logs the success message.
        with self.assertLogs(my_client.logger, level='INFO'):
            # Skip to timestamp.
            my_client.skip_to_timestamp(1, 2, 3)

    @patch('client.requests')
    def test_skip_to_timestamp_failure(self, mock_requests):
        """ Test the skip_to_timestamp method of the Client class,
        when the server returns a failed response."""

        # Simulate a failed request.
        mock_requests.post.return_value.status_code = 404
        mock_requests.post.return_value.json.return_value = {'error': 'Failed to skip to timestamp'}

        # Create an instance of Client class.
        my_client = Client()

        # Set the client ID.
        my_client.client_id = 456

        # Call the method and check if it logs the error message
        with self.assertLogs(my_client.logger, level='ERROR'):
            # Skip to timestamp.
            my_client.skip_to_timestamp(4, 5, 6)

    @patch('client.requests.get')
    def test_stop_streaming_movie_success(self, mock_get):
        """ Test the stop_streaming_movie method of the Client class,
        when the server returns a successful response."""

        # Create an instance of Client class.
        my_client = Client()

        # Set client_id to valid values.
        my_client.client_id = 1

        # Set selected_movie_id to valid values.
        my_client.set_selected_movie_id(123)

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Successfully stopped streaming'}
        mock_get.return_value = mock_response

        # Redirect console output to a StringIO object for message capture.
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Stop streaming the movie.
            my_client.stop_streaming_movie()

            # Check if the success message is printed to the console.
            self.assertEqual(mock_stdout.getvalue().strip(), 'Successfully stopped streaming')

    @patch('client.requests.get')
    def test_stop_streaming_movie_failure(self, mock_get):
        """ Test the stop_streaming_movie method of the Client class,
        when the server returns a failed response."""

        # Create an instance of Client class.
        my_client = Client()

        # Set client_id to valid values.
        my_client.client_id = 1

        # Set selected_movie_id to valid values.
        my_client.set_selected_movie_id(123)

        # Mock the server response for a failed request.
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Failed to stop streaming'}
        mock_get.return_value = mock_response

        # Redirect console output to a StringIO object for error message capture.
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Stop streaming the movie.
            my_client.stop_streaming_movie()

            # Check if the error message is printed to the console.
            self.assertEqual(mock_stdout.getvalue().strip(), 'Error: Failed to stop streaming')

    @patch('client.requests.get')
    @patch('client.filedialog.asksaveasfilename')
    @patch('client.showinfo')
    def test_download_project_portfolio_success(self, mock_showinfo, mock_asksaveasfilename, mock_get):
        """ Test the download_project_portfolio method of the Client class,
        when the server returns a successful response."""

        # Create an instance of Client class.
        my_client = Client()
        my_client.server_url = 'http://example.com'

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'Mock portfolio content'
        mock_get.return_value = mock_response

        # Mock the file dialog to return a valid file path.
        mock_asksaveasfilename.return_value = 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/project_portfolio.docx'

        # Download the project portfolio.
        my_client.download_project_portfolio()

        # Check if the 'showinfo' function was called with the correct message.
        mock_showinfo.assert_called_once_with(
            title='Information',
            message='File downloaded and saved to:\n'
                    'C:/Users/skfir/PycharmProjects/VOD_Server/assets/project_portfolio.docx'
        )

    @patch('client.requests.get')
    @patch('client.filedialog.asksaveasfilename')
    @patch('client.showinfo')
    def test_download_project_portfolio_failure(self, mock_showinfo, mock_asksaveasfilename, mock_get):
        """ Test the download_project_portfolio method of the Client class,
        when the server returns a failed response."""

        # Create an instance of Client class.
        my_client = Client()
        my_client.server_url = 'http://example.com'

        # Mock the server response for a failed request.
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Mock the file dialog to return None (user cancels the file dialog).
        mock_asksaveasfilename.return_value = None

        # Download the project portfolio.
        my_client.download_project_portfolio()

        # Check if the 'showinfo' function was called with the correct error message.
        mock_showinfo.assert_called_once_with(
            title='Information',
            message='Error downloading file. Status code: 404'
        )

    @patch('client.requests')
    def test_notify_server_on_exit_while_not_streaming(self, mock_requests):
        """ Test the notify_server_on_exit method of the Client class, when the client is not streaming a movie."""

        # Simulate a successful request.
        mock_requests.post.return_value.status_code = 200

        # Create an instance of Client class.
        my_client = Client()

        # Notify the server on exit.
        my_client.notify_server_on_exit()

        # Use assertLogs to check for 'INFO' logs
        with self.assertLogs(my_client.logger, level='INFO'):
            # Notify the server on exit.
            my_client.notify_server_on_exit()

    @patch('client.requests')
    def test_notify_server_on_exit_while_streaming(self, mock_requests):
        """ Test the notify_server_on_exit method of the Client class, when the client is streaming a movie."""

        # Simulate a successful request.
        mock_requests.post.return_value.status_code = 201

        # Create an instance of Client class.
        my_client = Client()

        # Notify the server on exit.
        my_client.notify_server_on_exit()

        # Use assertLogs to check for 'INFO' logs
        with self.assertLogs(my_client.logger, level='INFO'):
            my_client.notify_server_on_exit()

    @patch('client.requests')
    def test_notify_server_on_exit_failure(self, mock_requests):
        """ Test the notify_server_on_exit method of the Client class, when the server returns a failed response. """

        # Simulate a failed request.
        mock_requests.post.return_value.status_code = 404

        # Create an instance of Client class.
        my_client = Client()

        # Notify the server on exit.
        my_client.notify_server_on_exit()

        # Use assertLogs to check for 'ERROR' logs
        with self.assertLogs(my_client.logger, level='ERROR'):
            my_client.notify_server_on_exit()


########################################################################################################################
#                                Testing the settings area of the movie gallery window:                                #
########################################################################################################################


class TestClientFilterMoviesByGenre(unittest.TestCase):
    """ Test the filter_movies_by_genre method of the MovieGalleryWindow class. """

    @patch('client.requests.get')
    def setUp(self, mock_get):
        """ Create an instance of the MovieGalleryWindow class and initialize the necessary attributes."""
        # Create an instance of Client class.
        self.my_client = Client()

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Movie 1',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '01/01/2023',
                'rating': 1,
                'genre': 'Action',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Action-packed movie'
            },
            {
                'id': 2,
                'name': 'Movie 2',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '02/01/2023',
                'rating': 2,
                'genre': 'Adventure',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Adventure-packed movie'
            },
            {
                'id': 3,
                'name': 'Movie 3',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '03/01/2023',
                'rating': 3,
                'genre': 'Animated',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Animated-packed movie'
            },
            {
                'id': 4,
                'name': 'Movie 4',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '04/01/2023',
                'rating': 4,
                'genre': 'Comedy',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Comedy-packed movie'
            },
            {
                'id': 5,
                'name': 'Movie 5',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '05/01/2023',
                'rating': 5,
                'genre': 'Drama',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Drama-packed movie'
            },
            {
                'id': 6,
                'name': 'Movie 6',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '06/01/2023',
                'rating': 1,
                'genre': 'Fantasy',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Fantasy-packed movie'
            },
            {
                'id': 7,
                'name': 'Movie 7',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '07/01/2023',
                'rating': 2,
                'genre': 'History',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'History-packed movie'
            },
            {
                'id': 8,
                'name': 'Movie 8',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '08/01/2023',
                'rating': 3,
                'genre': 'Horror',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Horror-packed movie'
            },
            {
                'id': 9,
                'name': 'Movie 9',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '09/01/2023',
                'rating': 4,
                'genre': 'Musical',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Musical-packed movie'
            },
            {
                'id': 10,
                'name': 'Movie 10',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '10/01/2023',
                'rating': 5,
                'genre': 'Noir',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Noir-packed movie'
            },
            {
                'id': 11,
                'name': 'Movie 11',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '11/01/2023',
                'rating': 1,
                'genre': 'Romance',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Romance-packed movie'
            },
            {
                'id': 12,
                'name': 'Movie 12',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '12/01/2023',
                'rating': 2,
                'genre': 'Sci-Fi',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Sci-Fi-packed movie'
            },
            {
                'id': 13,
                'name': 'Movie 13',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '13/01/2023',
                'rating': 3,
                'genre': 'Thriller',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Thriller-packed movie'
            },
            {
                'id': 14,
                'name': 'Movie 14',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '14/01/2023',
                'rating': 4,
                'genre': 'Western',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Western-packed movie'
            }
        ]

        # Mock the server response for a successful request.
        mock_get.return_value = mock_response

        # Call the method to get movies from the server.
        self.my_client.get_movies_from_server()

        # Create an instance of your client class and initialize the necessary attributes.
        self.my_movie_gallery_window = MovieGalleryWindow(root, main_window_to_export)

        # Create a list of movie buttons.
        for movie in self.my_client.movies:
            self.my_movie_gallery_window.movie_buttons.append(self.my_movie_gallery_window.create_movie_button(movie))

        # Set the movie_buttons attribute of the MovieGalleryWindow class to the list of movie buttons.
        self.my_movie_gallery_window.filtered_movies = []

    def test_filter_movies_by_genre(self):
        """ Test the filter_movies_by_genre method of the MovieGalleryWindow class. """
        for selected_genre in ['All', 'Action', 'Adventure', 'Animated', 'Comedy', 'Drama', 'Fantasy', 'History',
                               'Horror', 'Musical', 'Noir', 'Romance', 'Sci-Fi', 'Thriller', 'Western']:
            # Filter the movies by genre.
            self.my_movie_gallery_window.filter_movies_by_genre(selected_genre)
            # Assert that only movie buttons with the selected genre are included in filtered_movies.
            expected_movie_buttons = [
                btn for btn in self.my_movie_gallery_window.movie_buttons if
                (btn.movie_genre == selected_genre or selected_genre == 'All')
            ]
            # Assert that the number of movie buttons in filtered_movies is equal to the expected number.
            self.assertEqual(len(self.my_movie_gallery_window.filtered_movies), len(expected_movie_buttons))
            if selected_genre == 'All':
                self.assertEqual(len(self.my_movie_gallery_window.filtered_movies), 14)
            else:
                self.assertEqual(len(self.my_movie_gallery_window.filtered_movies), 1)


class TestClientSortMovies(unittest.TestCase):
    """ Test the sort_movies method of the MovieGalleryWindow class. """

    @patch('client.requests.get')
    def setUp(self, mock_get):
        """ Create an instance of the MovieGalleryWindow class and initialize the necessary attributes."""
        # Create an instance of Client class.
        self.my_client = Client()

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Movie 1',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '01/01/2023',
                'rating': 1,
                'genre': 'Action',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Action-packed movie'
            },
            {
                'id': 2,
                'name': 'Movie 2',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '02/01/2023',
                'rating': 2,
                'genre': 'Adventure',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Adventure-packed movie'
            },
            {
                'id': 3,
                'name': 'Movie 3',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '03/01/2023',
                'rating': 3,
                'genre': 'Animated',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Animated-packed movie'
            },
            {
                'id': 4,
                'name': 'Movie 4',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '04/01/2023',
                'rating': 4,
                'genre': 'Comedy',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Comedy-packed movie'
            },
            {
                'id': 5,
                'name': 'Movie 5',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '05/01/2023',
                'rating': 5,
                'genre': 'Drama',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Drama-packed movie'
            }
        ]
        # Mock the server response for a successful request.
        mock_get.return_value = mock_response
        # Call the method to get movies from the server.
        self.my_client.get_movies_from_server()
        # Create an instance of your client class and initialize the necessary attributes.
        self.my_movie_gallery_window = MovieGalleryWindow(root, main_window_to_export)
        # Create a list of movie buttons.
        for movie in self.my_client.movies:
            self.my_movie_gallery_window.movie_buttons.append(self.my_movie_gallery_window.create_movie_button(movie))

    def test_sort_movies(self):
        """ Test the sort_movies method of the MovieGalleryWindow class. """
        # Create the expected movie button lists for each sort option.
        expected_oldest = expected_a_z = [
            self.my_movie_gallery_window.movie_buttons[0],
            self.my_movie_gallery_window.movie_buttons[1],
            self.my_movie_gallery_window.movie_buttons[2],
            self.my_movie_gallery_window.movie_buttons[3],
            self.my_movie_gallery_window.movie_buttons[4]
        ]
        expected_latest = expected_rating = expected_z_a = [
            self.my_movie_gallery_window.movie_buttons[4],
            self.my_movie_gallery_window.movie_buttons[3],
            self.my_movie_gallery_window.movie_buttons[2],
            self.my_movie_gallery_window.movie_buttons[1],
            self.my_movie_gallery_window.movie_buttons[0]
        ]
        # Loop through the selected sort options.
        for selected_sort in ['A-Z', 'Z-A', 'Rating', 'Latest', 'Oldest']:
            # Sort the movies by the selected sort.
            self.my_movie_gallery_window.sort_movies(selected_sort)
            # Assert that the movie buttons are sorted correctly.
            if selected_sort == 'A-Z':
                self.assertEqual(self.my_movie_gallery_window.movie_buttons, expected_a_z)
            elif selected_sort == 'Z-A':
                self.assertEqual(self.my_movie_gallery_window.movie_buttons, expected_z_a)
            elif selected_sort == 'Rating':
                self.assertEqual(self.my_movie_gallery_window.movie_buttons, expected_rating)
            elif selected_sort == 'Latest':
                self.assertEqual(self.my_movie_gallery_window.movie_buttons, expected_latest)
            elif selected_sort == 'Oldest':
                self.assertEqual(self.my_movie_gallery_window.movie_buttons, expected_oldest)


class TestClientSearchMovies(unittest.TestCase):
    """ Test the search_movies method of the MovieGalleryWindow class. """

    @patch('client.requests.get')
    def setUp(self, mock_get):
        """ Create an instance of the MovieGalleryWindow class and initialize the necessary attributes."""
        # Create an instance of Client class.
        self.my_client = Client()

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Movie 1',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '01/01/2023',
                'rating': 1,
                'genre': 'Action',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Action-packed movie'
            },
            {
                'id': 2,
                'name': 'Movie 2',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '02/01/2023',
                'rating': 2,
                'genre': 'Adventure',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Adventure-packed movie'
            },
            {
                'id': 3,
                'name': 'Movie 3',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '03/01/2023',
                'rating': 3,
                'genre': 'Animated',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Animated-packed movie'
            },
            {
                'id': 4,
                'name': 'Movie 4',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '04/01/2023',
                'rating': 4,
                'genre': 'Comedy',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Comedy-packed movie'
            },
            {
                'id': 5,
                'name': 'Movie 5',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '05/01/2023',
                'rating': 5,
                'genre': 'Drama',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Drama-packed movie'
            }
        ]

        # Mock the server response for a successful request.
        mock_get.return_value = mock_response

        # Call the method to get movies from the server.
        self.my_client.get_movies_from_server()

        # Create an instance of your client class and initialize the necessary attributes.
        self.my_movie_gallery_window = MovieGalleryWindow(root, main_window_to_export)

        # Create a list of movie buttons.
        for movie in self.my_client.movies:
            self.my_movie_gallery_window.movie_buttons.append(self.my_movie_gallery_window.create_movie_button(movie))

    def test_search_movies(self):
        """ Test the search_movies method of the MovieGalleryWindow class. """

        # Create the expected movie button lists for each search option.
        expected_movies_searched_movie = [
            self.my_movie_gallery_window.movie_buttons[0],
            self.my_movie_gallery_window.movie_buttons[1],
            self.my_movie_gallery_window.movie_buttons[2],
            self.my_movie_gallery_window.movie_buttons[3],
            self.my_movie_gallery_window.movie_buttons[4]
        ]
        expected_movies_searched_1 = [self.my_movie_gallery_window.movie_buttons[0]]
        expected_movies_searched_not_exists = []

        # Loop through the texts to search.
        for text_to_search in ['Movie', '1', 'Not Exists']:

            # Insert the text to search into the search box.
            self.my_movie_gallery_window.search_box.insert(0, text_to_search)

            # Search the movies by the selected text.
            self.my_movie_gallery_window.search_movies(event=None)

            # Assert that the searched results are correct.
            if text_to_search == 'Movie':
                self.assertEqual(len(expected_movies_searched_movie), 5)
                self.assertEqual(len(self.my_movie_gallery_window.search_in), len(expected_movies_searched_movie))
            elif text_to_search == '1':
                self.assertEqual(len(expected_movies_searched_1), 1)
                self.assertEqual(len(self.my_movie_gallery_window.search_in), len(expected_movies_searched_1))
            elif text_to_search == 'Not Exists':
                self.assertEqual(len(expected_movies_searched_not_exists), 0)
                self.assertEqual(len(self.my_movie_gallery_window.search_in), len(expected_movies_searched_not_exists))

            # Clear the search box.
            self.my_movie_gallery_window.search_box.delete(0, tk.END)

########################################################################################################################
#                                          Testing the selected movie window:                                          #
########################################################################################################################


class TestSelectedMovieWindow(unittest.TestCase):
    """ Test the SelectedMovieWindow class. """
    def setUp(self):
        """ Set up the test environment. """
        # Create an instance of Client class.
        self.my_client = Client()

        # Create an instance of SelectedMovieWindow class.
        self.selected_movie_window = SelectedMovieWindow(root, main_window_to_export)

    def test_create_layout_frames(self):
        """ Test the create_layout_frames method of the SelectedMovieWindow class. """
        # Check if the frames are created.
        self.assertIsNotNone(self.selected_movie_window.back_frame)
        self.assertIsNotNone(self.selected_movie_window.top_back_frame)
        self.assertIsNotNone(self.selected_movie_window.left_top_back_frame)
        self.assertIsNotNone(self.selected_movie_window.right_top_back_frame)
        self.assertIsNotNone(self.selected_movie_window.right_top_back_frame1)
        self.assertIsNotNone(self.selected_movie_window.right_top_back_frame2)
        self.assertIsNotNone(self.selected_movie_window.right_top_back_frame3)
        self.assertIsNotNone(self.selected_movie_window.bottom_back_frame)

    def test_create_labels_inside_frames(self):
        """ Test the create_labels_inside_frames method of the SelectedMovieWindow class. """
        # Check if the labels are created.
        self.assertIsNotNone(self.selected_movie_window.movie_image_label)
        self.assertIsNotNone(self.selected_movie_window.movie_name_label)
        self.assertIsNotNone(self.selected_movie_window.movie_date_label)
        self.assertIsNotNone(self.selected_movie_window.movie_length_label)
        self.assertIsNotNone(self.selected_movie_window.movie_rating_label)
        self.assertIsNotNone(self.selected_movie_window.movie_genre_label)
        self.assertIsNotNone(self.selected_movie_window.movie_description_scrolled_text)

    def test_create_buttons_inside_frames(self):
        """ Test the create_buttons_inside_frames method of the SelectedMovieWindow class. """
        # Check if the buttons are created.
        self.assertIsNotNone(self.selected_movie_window.play_button)
        self.assertIsNotNone(self.selected_movie_window.cancel_button)

    @patch('client.requests.get')
    def test_config_movie_labels(self, mock_get):
        """ Test the config_movie_labels method of the SelectedMovieWindow class. """

        # Mock the server response for a successful request.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Movie 1',
                'poster_location': 'C:/Users/skfir/PycharmProjects/VOD_Server/assets/Dogs.png',
                'date': '01/01/2023',
                'rating': 1,
                'genre': 'Action',
                'length_seconds_int': 3600,
                'length_hhmmss_string': '01:00:00',
                'description': 'Action-packed movie'
            }
        ]

        # Mock the server response for a successful request.
        mock_get.return_value = mock_response

        # Get movies from the server.
        self.my_client.get_movies_from_server()
        # Set the selected movie ID to 1.
        self.my_client.set_selected_movie_id(1)
        # Config the labels - Update the labels according to the selected movie.
        self.selected_movie_window.config_movie_labels(self.my_client.get_selected_movie_data())
        # Check if labels are set correctly.
        self.assertEqual(self.selected_movie_window.movie_name_label.cget("text"), 'Movie 1')
        self.assertEqual(self.selected_movie_window.movie_date_label.cget("text"), 'Released on 01/01/2023')
        self.assertEqual(self.selected_movie_window.movie_length_label.cget("text"), '01:00:00')


########################################################################################################################
#                                          Testing the movie player window:                                            #
########################################################################################################################


class TestMoviePlayerWindow(unittest.TestCase):

    def setUp(self):
        # Create an instance of Client class.
        self.my_client = Client()

        # Create an instance of SelectedMovieWindow class.
        self.movie_player_window = MoviePlayerWindow(root, main_window_to_export)

    def test_player_initialization(self):
        # Ensure that the player is properly initialized
        self.assertIsNotNone(self.movie_player_window.movie_player_frame)
        self.assertIsNotNone(self.movie_player_window.playback_controls_frame)
        self.assertIsNotNone(self.movie_player_window.instance)
        self.assertIsNotNone(self.movie_player_window.player)


if __name__ == '__main__':
    unittest.main()
