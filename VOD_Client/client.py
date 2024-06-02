########################################################################################################################
#                                                        Notes:                                                        #
########################################################################################################################
#                                                                                                                      #
#   - This file contains the client side of the VOD application.                                                       #
#     It is a GUI application that allows the user to browse a list of movies and watch them.                          #
#   - This file contains the following classes:                                                                        #
#     - Client:                                                                                                        #
#       This class represents a client of the movie server.                                                            #
#       It contains methods for connecting to the server, receiving the available movie data and streaming a movie.    #
#     - MainWindow:                                                                                                    #
#       This class represents the main window of the application.                                                      #
#       It initializes the main window, sets the title, and defines a window list of frames                            #
#       that are used to switch between windows, where each frame is a different type of window.                       #
#     - BaseWindow:                                                                                                    #
#       This is a base class for other windows in the application.                                                     #
#       It contains common methods for showing and hiding window frames.                                               #
#       This class inherits from the ttk.Frame class.                                                                  #
#     - MovieGalleryWindow:                                                                                            #
#       This class represents a window that displays a gallery of movies that are available to watch.                  #
#       It includes a search bar, a dropdown menu for selecting a genre, and a dropdown menu for sorting the movies.   #
#       Users can select a movie to view its details, or click the 'Information' button to view the project portfolio. #
#     - SelectedMovieWindow:                                                                                           #
#       This class represents a window that displays information about a selected movie.                               #
#       It includes movie details such as title, release date, length, rating, and description.                        #
#       Users can choose to play the selected movie or go back to the movie gallery.                                   #
#     - MoviePlayerWindow:                                                                                             #
#       This class represents a window that plays the selected movie.                                                  #
#       It includes a movie player, a progress bar, and buttons for controlling the movie playback.                    #
#       Users can pause, resume, skip, and stop the movie.                                                             #
#     - InformationWindow:                                                                                             #
#       This class represents a window that displays information about the project.                                    #
#       It includes the project portfolio and a button for downloading it.                                             #
#                                                                                                                      #
########################################################################################################################

import atexit
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Icon
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText

import vlc
import emoji
import requests
import time
import threading
import logging
from datetime import datetime
from PIL import Image, ImageTk

""" Constants and global variables """
MOVIE_GALLERY_WINDOW = 0
SELECTED_MOVIE_WINDOW = 1
MOVIE_PLAYER_WINDOW = 2
INFORMATION_WINDOW = 3
SERVER_URL = 'http://localhost:5000'
main_window_to_export = None
root = None


########################################################################################################################
#                                The following part handles Client-Server communication.                               #
########################################################################################################################


class Client:
    """ This class represents a client of the movie server.
    It contains methods for connecting to the server, receiving the available movie data and streaming a movie.

    Instance Attributes:

            client_id:
                (int) A unique identifier for the client.

            movies:
                (list) A list of movie data dictionaries.

            selected_movie_id:
                (int) The id of the selected movie.

            selected_movie_length_in_seconds_as_integer:
                (int) The length of the selected movie in seconds.

            streaming_requests_counter:
                (int) The number of streaming requests made by the client.

            rtp_url:
                (str) The RTP URL of the movie, received from the server.
    """

    def __init__(self):
        """ This method initializes the client object. """

        # A unique identifier for the client.
        self.client_id = 0

        # A list of movie data dictionaries.
        self.movies = []

        # The id of the selected movie.
        self.selected_movie_id = 0

        # The length of the selected movie in seconds.
        self.selected_movie_length_in_seconds_as_integer = 0

        # The number of streaming requests made by the client.
        self.streaming_requests_counter = 0

        # The RTP URL of the movie, received from the server.
        self.rtp_url = ''

        # Initialize the logger
        self.logger = logging.getLogger(__name__)

    def connect_client_to_server(self):
        """ This method sends a 'GET' request to the server to connect a new client.
        The server returns a unique client id that is stored in the client_id attribute. """

        # Send a 'GET' request to the server to connect a new client.
        response = requests.get(f'{SERVER_URL}/connect_new_client_to_server')

        # Store the client id received from the server.
        self.client_id = response.json().get('client_id')

    def get_movies_from_server(self):
        """ This method sends a 'GET' request to the server to receive the movie list.
        The server returns a list of movie data dictionaries that are stored in the 'movies' attribute.
        If the request was unsuccessful, an error message is printed to the console.

        Each movie data dictionary contains the following keys:

            'id':
                (int) The movie id.

            'name':
                (str) The movie name.

            'poster_location':
                (str) The movie poster location.

            'date':
                (str) The movie release date in the format 'DD/MM/YYYY'.

            'rating':
                (int) The movie rating.

            'genre':
                (str) The movie genre.

            'length_seconds_int':
                (int) The movie length in seconds as an integer.

            'length_hhmmss_string':
                (str) The movie length in the format 'HH:MM:SS'.

            'description':
                (str) The movie description.
        """

        # Send a 'GET' request to the server to receive the movie list.
        response = requests.get(f'{SERVER_URL}/get_movies')

        # Check if the request was successful.
        if response.status_code == 200:

            # Store the movie list received from the server.
            self.movies = response.json()

        else:
            print('Error:', response.json().get('error'))

    def get_movie_list(self):
        """ This method returns the movie list."""

        # Return the movie list.
        return self.movies

    def increase_streaming_requests_counter(self):
        """ This method increases the streaming_requests_counter attribute by 1."""

        # Increase the streaming_requests_counter attribute by 1.
        self.streaming_requests_counter += 1

    def get_streaming_requests_counter(self):
        """ This method returns the streaming_requests_counter attribute. """

        # Return the streaming_requests_counter attribute.
        return self.streaming_requests_counter

    def set_selected_movie_id(self, movie_id):
        """ This method sets the selected_movie_id attribute to the given movie_id. """

        # Set the selected_movie_id attribute to the given movie_id.
        self.selected_movie_id = movie_id

    def get_selected_movie_data(self):
        """ This method returns the movie data dictionary of the selected movie.
        When the movie is found, the selected_movie_length_in_seconds_as_integer attribute is set to the movie length.
        This attribute is used to calculate the remaining time in the movie player window.
        """
        selected_movie = self.movies[self.selected_movie_id - 1]
        self.selected_movie_length_in_seconds_as_integer = selected_movie["length_seconds_int"]
        return selected_movie

    def get_selected_movie_length_in_seconds_as_integer(self):
        """ This method returns the selected_movie_length_in_seconds_as_integer attribute. """

        # Return the selected_movie_length_in_seconds_as_integer attribute.
        return self.selected_movie_length_in_seconds_as_integer

    def get_movie_rtp_url(self):
        """ This method sends a 'POST' request to the server to set the chosen movie.
        The server returns the RTP URL of the movie, which is stored in the rtp_url attribute.
        If the request was unsuccessful, an error message is printed to the console.
        """

        # Send a 'POST' request to the server to set the chosen movie.
        response = requests.post(f'{SERVER_URL}/get_movie_rtp_url/{self.client_id}/{self.selected_movie_id}')

        # Check if the request was successful.
        if response.status_code == 200:

            # Store the RTP URL of the movie.
            self.rtp_url = response.json().get('rtp_url')

            # Return the RTP URL of the movie.
            return self.rtp_url
        else:
            print('Error:', response.json().get('error'))

    def stop_streaming_movie(self):
        """ This method sends a 'GET' request to the server to stop streaming the current movie.
        If the request was unsuccessful, an error message is printed to the console. """

        # Send a 'GET' request to the server to stop streaming the current movie.
        response = requests.get(f'{SERVER_URL}/stop_streaming/{self.client_id}/{self.selected_movie_id}')

        # Check if the request was successful.
        if response.status_code == 200:
            # Display the server's response
            print(response.json().get('message'))
        else:
            print('Error:', response.json().get('error'))

    def download_project_portfolio(self):
        """ This method sends a 'GET' request to the server to download the project portfolio.
        The server returns the project portfolio file, which is saved to the user's computer.
        If the request was unsuccessful, an error message is printed to the console."""

        # Send a 'GET' request to the server to download the project portfolio.
        response = requests.get(f'{SERVER_URL}/download_project_portfolio')

        # Check if the request was successful.
        if response.status_code == 200:
            # Prompt the user to choose where to save the file.
            file_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word Files", "*.docx")],
                title="Save Project Portfolio",
                initialfile="project_portfolio.docx",
            )
            # Check if the user canceled the file dialog.
            if file_path:
                # Save the downloaded content to the chosen file location.
                with open(file_path, 'wb') as file:
                    file.write(response.content)

                # Display a popup message to the user.
                showinfo(
                    title='Information',
                    message=f'File downloaded and saved to:\n{file_path}'
                )
            else:
                # Display a popup message to the user.
                showinfo(
                    title='Information',
                    message='File download canceled by the user'
                )
        else:
            print(f'Error downloading file. Status code: {response.status_code}')
            # Display a popup message to the user.
            showinfo(
                title='Information',
                message=f'Error downloading file. Status code: {response.status_code}'
            )

    def notify_server_on_exit(self):
        """ This method sends a 'POST' request to the server to notify it that the client is exiting.
        If the request was unsuccessful, an error message is printed to the console.
        This method is called when the client exits the application. """
        try:
            # Send a 'POST' request to the server to notify it that the client is exiting.
            response = requests.post(f'{SERVER_URL}/client_exit/{self.client_id}')

            # Check if the request was successful.
            if response.status_code == 200:
                self.logger.info(
                    "Client exit notification successful: %s",
                    response.json().get('message')
                )
            elif response.status_code == 201:
                self.logger.info(
                    f'Client {self.client_id} has exited unexpectedly and stopped the movie streaming: %s',
                    response.status_code
                )
            elif response.status_code == 404:
                self.logger.error(
                    f'Client {self.client_id} not found: %s',
                    response.status_code
                )
        except Exception as e:
            self.logger.error('Error notifying server of client exit: %s', str(e))

    def start_streaming_movie(self):
        """ This method sends a 'POST' request to the server to start streaming the chosen movie.
        If the request was unsuccessful, an error message is printed to the console. """

        # Send a 'POST' request to the server to start streaming the chosen movie.
        response = requests.post(f'{SERVER_URL}/start_streaming/{self.client_id}')

        # Check if the request was successful.
        if response.status_code == 200:
            print(response.json().get('message'))
            self.logger.info(
                response.json().get('message')
            )
        else:
            print('Error:', response.json().get('error'))
            self.logger.error(
                response.json().get('error')
            )

    def skip_to_timestamp(self, hours, minutes, seconds):
        """ This method sends a 'POST' request to the server to skip to the specified timestamp in the selected movie
        playback. If the request was unsuccessful, an error message is printed to the console."""

        # Send a request to the server to skip to the specified timestamp.
        response = requests.post(
            f'{SERVER_URL}/skip_to_timestamp/{self.client_id}/{hours:02}:{minutes:02}:{seconds:02}'
        )
        # Check if the request was successful.
        if response.status_code == 200:
            print(response.json().get('message'))
            self.logger.info(
                response.json().get('message')
            )
        else:
            print('Error:', response.json().get('error'))
            self.logger.error(
                response.json().get('error')
            )


# Create a global client object to be used by all windows in the application.
client = Client()


########################################################################################################################
#                                     The following part handles Window management.                                    #
########################################################################################################################


class MainWindow:
    """ This class represents the main window of the application.
    It initializes the main window, sets the title, and defines a window list of frames
    that are used to switch between windows, where each frame is a different type of window.
    Instance Attributes:

            master:
                (tkinter.Tk) The main window.

            window_frame_list:
                (list) A list of window frames.

            current_window_frame:
                (ttk.Frame) The current window frame.
    """

    def __init__(self, master):
        """ This method initializes the main window. """

        # Set the master window
        self.master = master

        # Set the title of the window
        self.master.title("Project: VOD Movie Server    |    By: Kfir Sibirsky")

        # Set the position of the window to the center of the screen.
        center_window(self, 800, 600)

        # Disable resizing the window.
        self.master.resizable(False, False)

        # Configure grid layout.
        self.master.grid_rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Create the list of window frames.
        self.window_frame_list = [
            # `root` is passed as `self.master` and `main_window` is passed as `self` (in each of the following lines)
            MovieGalleryWindow(self.master, self),
            SelectedMovieWindow(self.master, self),
            MoviePlayerWindow(self.master, self),
            InformationWindow(self.master, self),
        ]

        # Set and show the current window frame to the first window frame in the list.
        self.current_window_frame = self.window_frame_list[0]
        self.current_window_frame.show()

        # Bind the window closing event to the on_closing method.
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def switch_windows(self, window_number):
        """ This method is used to switch between frames.
         It hides the current frame and shows the frame in the window_frame_list at the given index.
         Based on the type of the window frame to switch to,
         it might call an additional method to update the content of that window frame.

         Parameter:
            window_number:
                (int) The index of the window frame in the window_frame_list to switch to.
         """

        # Hide the current window frame.
        self.current_window_frame.hide()

        # Update the current window frame to the new window frame at the given index.
        self.current_window_frame = self.window_frame_list[window_number]

        # Update the content of the window frame if needed
        if window_number == SELECTED_MOVIE_WINDOW:
            self.current_window_frame.config_movie_labels(test_movie_data=None)
        elif window_number == MOVIE_PLAYER_WINDOW:
            self.current_window_frame.start_movie_player()

        # Show the (newly) current window frame
        self.current_window_frame.show()

    def on_closing(self):
        """ This method handles the window closing event. """

        # Destroy the window.
        self.master.destroy()


class BaseWindow(ttk.Frame):
    """ This is a base class for other windows in the application.
    It contains common methods for showing and hiding window frames.
    This class inherits from the ttk.Frame class.

    Instance Attributes:

            master:
                (tkinter.Tk) The main window.

            main_window:
                (MainWindow) The main window of the application.
    """

    def __init__(self, master, main_window):
        """ This method initializes the window. """

        # Call the parent class constructor.
        super().__init__(master)

        # Set the master window to the given master.
        self.master = master

        # Set the main window to the given main_window.
        self.main_window = main_window

        # Style the font in the widgets to Consolas.
        font_style = ttk.Style()
        font_style.configure("TLabel", font="Consolas 11")
        font_style.configure("TLabelframe.Label", font="Consolas 11")
        font_style.configure("TButton", font="Consolas 11", justify="center")
        font_style.configure("TEntry", font="Consolas 11")
        font_style.configure("TEntry.Text", font="Consolas 11")
        font_style.configure("TMenubutton", font="Consolas 11")
        font_style.configure("TRadiobutton", font="Consolas 11")
        font_style.configure("TFrame", font="Consolas 11")

    def show(self):
        """ Method for showing windows. """

        # Show the window
        self.grid(row=0, column=0, sticky="nsew")

    def hide(self):
        """ Method for hiding windows. """

        # Hide the window
        self.grid_forget()


class MovieGalleryWindow(BaseWindow):
    """ This class represents a window that displays a gallery of movies that are available to watch.
     It includes a search bar, a dropdown menu for selecting a genre, and a dropdown menu for sorting the movies.
     Users can select a movie to view its details, or click the 'Information' button to view the project portfolio. """

    def __init__(self, master, main_window):
        """ This method initializes the movie gallery window. """

        # Call the parent class constructor.
        super().__init__(master, main_window)

        self.movies_labelframe = None
        self.scrollable_frame = None
        self.movie_list = None
        self.search_in = None
        self.movie_buttons = None
        self.filtered_movies = None
        self.sorting_item_var = None
        self.search_box = None
        self.genre_item_var = None
        self.settings_label_frame = None

        # Create the settings area.
        self.create_settings_area()

        # Create the movies area.
        self.create_movies_area()

    def create_settings_area(self):
        # Create a label frame widget for the settings.
        self.settings_label_frame = ttk.LabelFrame(self, text=" Settings ", width=800, height=100)
        self.settings_label_frame.pack_propagate(False)
        self.settings_label_frame.pack(padx=20, pady=15, fill=ttk.BOTH, expand=True)

        # Create the genre area and calculate its width.
        genre_width = self.create_genre_selection_area()

        # Create the sorting area and calculate its width.
        sort_width = self.create_sorting_selection_area()

        # Create the search area.
        self.create_search_area()

        # Create the information area and calculate its width.
        info_width = self.create_information_area()

        # Calculate the width of the search box.
        search_width = self.settings_label_frame.winfo_width() - genre_width - sort_width - info_width

        # Set the width of the search box to fill the remaining space in the settings label frame.
        self.search_box.config(width=search_width)

    def create_genre_selection_area(self):
        # Create a label widget for the genre selection dropdown menu
        genre_label = ttk.Label(self.settings_label_frame, text=" Genre: ")
        genre_label.pack(side=ttk.LEFT, padx=5, pady=10)

        # Create a menu button for the genre selection
        genre_menu = ttk.Menubutton(self.settings_label_frame, text="All", style=SECONDARY)
        genre_menu.pack(side=ttk.LEFT, padx=5, pady=10)

        # Create a menu for the genre selection
        inside_genre_menu = ttk.Menu(genre_menu)

        # Create a variable to store the selected genre
        self.genre_item_var = StringVar()

        # Create a radio button for each genre option
        for genre_option in ['All', 'Action', 'Adventure', 'Animated', 'Comedy', 'Drama', 'Fantasy', 'History',
                             'Horror', 'Musical', 'Noir', 'Romance', 'Sci-Fi', 'Thriller', 'Western']:
            inside_genre_menu.add_radiobutton(
                label=genre_option,
                variable=self.genre_item_var,
                command=lambda genre=genre_option: [
                    genre_menu.config(text=genre),
                    self.filter_movies_by_genre(genre)
                ],
                font="Consolas 11"
            )

        # Set the menu of the genre selection menu button to the genre menu
        genre_menu['menu'] = inside_genre_menu

        # Bind the genre selection dropdown menu to the filter_movies_by_genre method
        self.genre_item_var.trace(
            "w",
            lambda *args: self.filter_movies_by_genre(self.genre_item_var.get())
        )
        # Return the width of the genre selection dropdown menu.
        return genre_label.winfo_reqwidth() + genre_menu.winfo_reqwidth()

    def filter_movies_by_genre(self, selected_genre):
        """ This method filters the movies by the selected genre.

        Parameters:
                selected_genre:
                    (str) The selected genre.

        """

        # Remove all movie buttons from the grid.
        self.remove_movie_buttons()

        # Clear the filtered movies list.
        self.filtered_movies = []

        # Filter the movies by the selected genre.
        for movie_btn in self.movie_buttons:
            movie_genre = movie_btn.movie_genre
            if selected_genre == "All" or movie_genre == selected_genre:
                self.filtered_movies.append(movie_btn)

        # Relayout the filtered movie buttons in the grid.
        self.relayout_filtered_buttons(self.filtered_movies)

    def create_sorting_selection_area(self):
        # Create a label widget for the sorting selection dropdown menu
        sorting_label = ttk.Label(self.settings_label_frame, text="Sort By: ")
        sorting_label.pack(side=ttk.LEFT, padx=5, pady=10)

        # Create a menu button for the sorting selection
        sorting_menu = ttk.Menubutton(self.settings_label_frame, text="A-Z", style=SECONDARY)
        sorting_menu.pack(side=ttk.LEFT, padx=5, pady=10)

        # Create a menu for the sorting selection
        inside_sorting_menu = ttk.Menu(sorting_menu)

        # Create a variable to store the selected sorting criteria
        self.sorting_item_var = StringVar()

        # Create a radio button for each sorting criteria option
        for sort_option in ['A-Z', 'Z-A', 'Rating', 'Latest', 'Oldest']:
            inside_sorting_menu.add_radiobutton(
                label=sort_option,
                variable=self.sorting_item_var,
                command=lambda sort=sort_option: [
                    sorting_menu.config(text=sort),
                    self.sort_movies(sort)
                ],
                font="Consolas 11"
            )

        # Set the menu of the sorting selection menu button to the sorting menu
        sorting_menu['menu'] = inside_sorting_menu

        # Bind the sorting selection dropdown menu to the sort_movies method
        self.sorting_item_var.trace("w", lambda *args: self.sort_movies(self.sorting_item_var.get()))
        # Return the width of the sorting selection dropdown menu.
        return sorting_label.winfo_reqwidth() + sorting_menu.winfo_reqwidth()

    def sort_movies(self, selected_sorting_criteria):
        """ This method sorts the movies by the selected sorting criteria.

        Parameters:
                selected_sorting_criteria:
                    (str) The selected sorting criteria.

        """

        # Remove all movie buttons from the grid.
        self.remove_movie_buttons()

        # Sort the filtered movies by the selected sorting criteria.
        if selected_sorting_criteria == "A-Z":
            self.filtered_movies.sort(key=lambda btn: btn.movie_name)
        elif selected_sorting_criteria == "Z-A":
            self.filtered_movies.sort(key=lambda btn: btn.movie_name, reverse=True)
        elif selected_sorting_criteria == "Rating":
            self.filtered_movies.sort(key=lambda btn: btn.movie_rating, reverse=True)
        elif selected_sorting_criteria == "Latest":
            self.filtered_movies.sort(key=lambda btn: datetime.strptime(btn.movie_date, '%d/%m/%Y'), reverse=True)
        elif selected_sorting_criteria == "Oldest":
            self.filtered_movies.sort(key=lambda btn: datetime.strptime(btn.movie_date, '%d/%m/%Y'))

        # Relayout the filtered movie buttons in the grid.
        self.relayout_filtered_buttons(self.filtered_movies)

    def create_search_area(self):
        # Create a label widget for the search box.
        search_label = ttk.Label(self.settings_label_frame, text="Search:")
        search_label.pack(side=ttk.LEFT, padx=5, pady=10)

        # Create an entry widget for the search box.
        self.search_box = ttk.Entry(
            self.settings_label_frame,
            style=SECONDARY,
            font="Consolas 11",
        )
        self.search_box.pack(fill=tk.X, expand=True, side=ttk.LEFT, padx=5, pady=10)

        # Bind the search box to the search_movies method.
        self.search_box.bind('<KeyRelease>', self.search_movies)

    def search_movies(self, event):
        """ This method filters the movies by the text entered the search box.

        Parameter:
                event:
                    (tkinter.Event) The event object.
        """

        # Remove all movie buttons from the grid.
        self.remove_movie_buttons()

        # Get the text entered the search box and convert to lowercase.
        search_text = self.search_box.get().lower()

        # Create a list to store filtered movies.
        self.search_in = []

        # Filter the movies by the text entered the search box.
        for movie_btn in self.filtered_movies:

            # Convert the movie name to lowercase.
            movie_name = movie_btn.movie_name.lower()

            # Check if the search text is in the movie name.
            if search_text in movie_name:
                self.search_in.append(movie_btn)

        # Relayout the filtered movie buttons in the grid.
        self.relayout_filtered_buttons(self.search_in)

    def create_information_area(self):
        """ This method creates a button widget for the information window. """
        # Create a button widget for the information window
        info_icon = PhotoImage(data=Icon.info)
        information_btn = ttk.Button(
            self.settings_label_frame,
            image=info_icon,
            style=LINK,
            cursor="hand2",
            command=lambda: self.main_window.switch_windows(INFORMATION_WINDOW),
        )
        information_btn.image = info_icon
        information_btn.pack(side=ttk.RIGHT, padx=5, pady=10)
        # Return the width of the information button.
        return information_btn.winfo_reqwidth()

    def remove_movie_buttons(self):
        """ This method removes all movie buttons from the grid. """
        for movie_btn in self.movie_buttons:
            movie_btn.grid_remove()

    def relayout_filtered_buttons(self, movies_list):
        """ This method relayouts the filtered movie buttons in the grid.

        Parameters:
                movies_list:
                    (list) A list of movie buttons.
        """
        _row, _col = 0, 0
        for movie_btn in movies_list:
            if _col == 3:
                _col = 0
                _row += 1
            movie_btn.grid(column=_col, row=_row, padx=5, pady=20)
            _col += 1

    def create_movies_area(self):
        # Create a label frame widget for the movies.
        self.movies_labelframe = ttk.LabelFrame(self, text=" Movies ", width=800, height=500)
        self.movies_labelframe.pack_propagate(False)
        self.movies_labelframe.pack(padx=20, pady=15, fill=ttk.BOTH, expand=True)

        # Create a scrollable frame widget for the movie buttons
        self.scrollable_frame = ScrolledFrame(self.movies_labelframe, autohide=False)
        self.scrollable_frame.pack(pady=10, fill=ttk.BOTH, expand=True)

        # Configure the columns of the scrollable frame
        for col in range(3):
            self.scrollable_frame.columnconfigure(col, weight=1)

        # Get the movie list from the server.
        self.movie_list = client.get_movie_list()

        # Initialize row and column values
        self.movie_buttons = []

        # List to store filtered movies
        self.filtered_movies = self.movie_buttons

        # Create a button widget for each movie in the movie list.
        self.create_movie_buttons()

    def create_movie_buttons(self):
        """ This method creates a button widget for each movie in the movie list. """
        # Create a button widget for each movie in the movie list.
        for index, movie_data in enumerate(self.movie_list):
            # Create a button widget for the movie.
            movie_button = self.create_movie_button(movie_data)
            # Add the button to the movie buttons list.
            self.movie_buttons.append(movie_button)
            # Calculate the row and column of the button in the grid.
            row, col = divmod(index, 3)
            # Add the button to the grid.
            movie_button.grid(column=col, row=row, padx=10, pady=20)

    def create_movie_button(self, movie_data):
        """ This method creates a button widget for the given movie data dictionary.

        Parameters:
                movie_data:
                    (dict) A movie data dictionary.

        """
        # Create a button widget for the movie.
        poster = ImageTk.PhotoImage(Image.open(movie_data["poster_location"]).resize((180, 230)))
        movie_text = movie_data["name"] + "\n" + movie_data["date"]
        movie_button = ttk.Button(
            self.scrollable_frame,
            image=poster,
            cursor="hand2",
            style=SECONDARY,
            text=movie_text,
            compound='top',
            command=lambda: [
                client.set_selected_movie_id(movie_data["id"]),
                self.main_window.switch_windows(SELECTED_MOVIE_WINDOW)
            ]
        )
        # Store references to avoid garbage collection.
        movie_button.image = poster
        movie_button.movie_genre = movie_data["genre"]
        movie_button.movie_rating = movie_data["rating"]
        movie_button.movie_name = movie_data["name"]
        movie_button.movie_date = movie_data["date"]
        return movie_button


class SelectedMovieWindow(BaseWindow):
    """ This class represents a window that displays information about a selected movie.
    It includes movie details such as title, release date, length, rating, and description.
    Users can choose to play the selected movie or go back to the movie gallery.

    Instance Attributes:

                back_frame:
                    (ttk.LabelFrame) A label frame widget for the movie data and users choice buttons.

                top_back_frame:
                    (ttk.Frame) A frame widget for the movie poster.

                left_top_back_frame:
                    (ttk.Frame) A frame widget for the movie details.

                right_top_back_frame:
                    (ttk.Frame) A frame widget for the movie details.

                bottom_back_frame:
                    (ttk.Frame) A frame widget for the user's choice buttons.

                movie_image_label:
                    (ttk.Label) A label widget for the movie poster.

                movie_name_label:
                    (ttk.Label) A label widget for the movie name.

                movie_date_label:
                    (ttk.Label) A label widget for the movie release date.

                movie_length_label:
                    (ttk.Label) A label widget for the movie length.

                movie_rating_label:
                    (ttk.Label) A label widget for the movie rating.

                movie_genre_label:
                    (ttk.Label) A label widget for the movie genre.

                movie_description_scrolled_text:
                    (ScrolledText) A scrolled text for the movie description.

                play_button:
                    (ttk.Button) A button widget for playing the movie.

                cancel_button:
                    (ttk.Button) A button widget for going back to the movie gallery.


    """

    def __init__(self, master, main_window):
        """ This method initializes the selected movie window. """

        # Call the parent class constructor.
        super().__init__(master, main_window)

        self.back_frame = None
        self.top_back_frame = None
        self.left_top_back_frame = None
        self.right_top_back_frame = None
        self.right_top_back_frame1 = None
        self.right_top_back_frame2 = None
        self.right_top_back_frame3 = None
        self.bottom_back_frame = None

        self.movie_image_label = None
        self.movie_name_label = None
        self.movie_date_label = None
        self.movie_length_label = None
        self.movie_rating_label = None
        self.movie_genre_label = None
        self.movie_description_scrolled_text = None

        self.play_button = None
        self.cancel_button = None

        # Create the layout frames.
        self.create_layout_frames()

        # Create the labels inside the frames.
        self.create_labels_inside_frames()

        # Create the buttons inside the frames.
        self.create_buttons_inside_frames()

    def create_layout_frames(self):
        # Create a label frame widget for the movie data and users choice buttons.
        self.back_frame = ttk.LabelFrame(self, text=" Movie Details ")
        self.back_frame.pack(padx=15, pady=15, fill=ttk.BOTH, expand=True)

        # Create a frame widget for the movie poster.
        self.top_back_frame = ttk.Frame(self.back_frame)
        self.top_back_frame.pack(fill=ttk.BOTH, expand=True)

        # Create a frame widget for the movie details.
        self.left_top_back_frame = ttk.Frame(self.top_back_frame)
        self.left_top_back_frame.pack(padx=15, pady=15, fill=ttk.Y, expand=True, side=ttk.LEFT, anchor=ttk.CENTER)

        # Create a frame widget for the movie details.
        self.right_top_back_frame = ttk.Frame(self.top_back_frame)
        self.right_top_back_frame.pack(padx=15, pady=15, fill=ttk.Y, expand=True, side=ttk.RIGHT, anchor=ttk.CENTER)

        # Create a frame widget for the movie details.
        self.right_top_back_frame1 = ttk.Frame(self.right_top_back_frame)
        self.right_top_back_frame1.pack(fill=ttk.BOTH, expand=True)

        # Create a frame widget for the movie rating stars.
        self.right_top_back_frame2 = ttk.Frame(self.right_top_back_frame)
        self.right_top_back_frame2.pack(anchor=tk.W)

        # Configure grid layout - each column is for one star.
        self.right_top_back_frame2.columnconfigure(0, weight=1)
        self.right_top_back_frame2.columnconfigure(1, weight=1)
        self.right_top_back_frame2.columnconfigure(2, weight=1)
        self.right_top_back_frame2.columnconfigure(3, weight=1)
        self.right_top_back_frame2.columnconfigure(4, weight=1)

        # Create a frame widget for the movie details.
        self.right_top_back_frame3 = ttk.Frame(self.right_top_back_frame)
        self.right_top_back_frame3.pack(fill=ttk.BOTH, expand=True)

        # Create a frame widget for the users choice buttons.
        self.bottom_back_frame = ttk.Frame(self.back_frame)
        self.bottom_back_frame.pack(fill=ttk.BOTH, expand=True)

    def create_labels_inside_frames(self):
        # Create a label widget for the movie poster.
        self.movie_image_label = ttk.Label(self.left_top_back_frame)
        self.movie_image_label.pack(expand=True, anchor=ttk.CENTER)

        # Create a label widget for the movie name.
        self.movie_name_label = ttk.Label(self.right_top_back_frame1, text="Title")
        self.movie_name_label.pack(fill=ttk.BOTH, expand=True)

        # Create a label widget for the movie release date.
        self.movie_date_label = ttk.Label(self.right_top_back_frame1, text="Year")
        self.movie_date_label.pack(fill=ttk.BOTH, expand=True)

        # Create a label widget for the movie length.
        self.movie_length_label = ttk.Label(self.right_top_back_frame1, text="Length")
        self.movie_length_label.pack(fill=ttk.BOTH, expand=True)

        # Create a label widget for the movie rating.
        self.movie_rating_label = ttk.Label(self.right_top_back_frame2, text="Rating")
        # self.movie_rating_label.pack(fill=ttk.BOTH, expand=True)

        # Create a label widget for the movie genre.
        self.movie_genre_label = ttk.Label(self.right_top_back_frame3, text="Genre")
        self.movie_genre_label.pack(fill=ttk.BOTH, expand=True)

        # Create a scrolled text for the movie description.
        self.movie_description_scrolled_text = ScrolledText(
            self.right_top_back_frame3,
            height=10,
            wrap=WORD,
            autohide=False
        )
        self.movie_description_scrolled_text.pack(fill=ttk.BOTH, expand=True)

    def create_buttons_inside_frames(self):
        # Create a button widget for playing the movie.
        self.play_button = ttk.Button(
            self.bottom_back_frame,
            text="Play Movie",
            command=lambda: self.main_window.switch_windows(MOVIE_PLAYER_WINDOW),
            cursor="hand2"
        )
        self.play_button.pack(padx=15, pady=15, side=ttk.LEFT, fill=ttk.BOTH, expand=True)

        # Create a button widget for going back to the movie gallery.
        self.cancel_button = ttk.Button(
            self.bottom_back_frame,
            text="Cancel",
            command=lambda: self.main_window.switch_windows(MOVIE_GALLERY_WINDOW),
            cursor="hand2"
        )
        self.cancel_button.pack(padx=15, pady=15, side=ttk.RIGHT, fill=ttk.BOTH, expand=True)

    def config_movie_labels(self, test_movie_data):
        """ This method configures the movie labels with the data of the selected movie.
        It is called when the user selects a movie in the movie gallery.

        Parameter:
            test_movie_data:
                (dict) A movie data dictionary that is used only for testing.
        """

        if test_movie_data:
            # Get the movie data of the selected movie from the unit test.
            cur_movie_data = test_movie_data
        else:
            # Get the movie data of the selected movie from the server through the client object.
            cur_movie_data = client.get_selected_movie_data()

        # Set the poster image to the movie poster and resize the image.
        poster = ImageTk.PhotoImage(Image.open(cur_movie_data['poster_location']).resize((365, 450)))
        self.movie_image_label.config(image=poster)
        self.movie_image_label.image = poster

        # Set the name label to the movie name.
        self.movie_name_label.config(text=cur_movie_data['name'])

        # Set the released date label to the movie release date.
        self.movie_date_label.config(text=f"Released on {cur_movie_data['date']}")

        # Set the length label to the movie length.
        self.movie_length_label.config(text=cur_movie_data['length_hhmmss_string'])

        # Set the rating label to the movie rating.
        five_stars_str = str(emoji.emojize(':star:')) * 5
        count_stars = 0
        for idx, letter in enumerate(five_stars_str):
            # Set the color of the star to white if the count_stars is less than the movie rating, otherwise gray.
            if count_stars < int(cur_movie_data['rating']):
                ttk.Label(self.right_top_back_frame2, text=letter, foreground='white', anchor="w").grid(row=0,
                                                                                                        column=idx)
            else:
                ttk.Label(self.right_top_back_frame2, text=letter, foreground='gray', anchor="w").grid(row=0,
                                                                                                       column=idx)
            count_stars += 1

        # Set the genre label to the movie genre.
        self.movie_genre_label.config(text=cur_movie_data['genre'])

        # Clear the scrolled text widget and insert the movie description.
        self.movie_description_scrolled_text.delete('1.0', END)
        self.movie_description_scrolled_text.insert(END, cur_movie_data['description'])
        self.movie_description_scrolled_text.text.config(font="Consolas 11")


def format_time(seconds):
    """ This method receives a number of seconds and returns a string in the format 'HH:MM:SS'.

    Parameter:
        seconds:
            (int) The number of seconds.

    Returns:
        (str) The formatted time string.

    Example:
        5025 seconds: 1 hour, 23 minutes, and 45 seconds.
        hours = 5025 / 3600 = 1.3958333333333333, so hours = 1
        remainder = 5025 % 3600 = 1425, so remainder = 1425
        minutes = 1425 / 60 = 23.75, so minutes = 23
        seconds = 1425 % 60 = 45, so seconds = 45
        The returned string is '01:23:45'.

    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


class MoviePlayerWindow(BaseWindow):
    """ This class represents a window that plays the selected movie.
    It includes sliders and buttons for controlling the playback/volume, toggling full-screen mode,
    as well as a label for displaying the elapsed/remaining time.
    Users can pause and resume the movie, skip to a specific time, and stop the movie.
    When the movie ends, the window is closed, and the user is returned to the movie gallery.

    Instance Attributes:

        controls_visible:
            (bool) A flag that indicates whether the controls are visible or not.

        fullscreen:
            (bool) A flag that indicates whether the window is in full-screen mode or not.

        play_pause_button:
            (ttk.Button) A button widget for pausing/resuming the movie.

        movie_started:
            (bool) A flag that indicates whether the movie has started playing or not.

        volume_slider:
            (ttk.Scale) A slider widget for controlling the volume.

        volume_mute_toggle_button:
            (ttk.Button) A button widget for toggling mute mode.

        time_update_thread:
            (threading.Thread) A thread used to update the elapsed/remaining time labels.

        stop_movie_event:
            (threading.Event) An event that is used to signal thread termination.

        movie_player_frame:
            (ttk.Frame) A frame widget for movie playback.

        instance:
            (vlc.Instance) A VLC instance.

        media:
            (vlc.Media) A VLC media object.

        player:
            (vlc.MediaPlayer) A VLC media player object.

        playback_controls_frame:
            (ttk.Frame) A frame widget for movie playback controls.

        movie_player_greeting_label:
            (ttk.Label) A label widget for the greeting message.

        elapsed_var:
            (ttk.StringVar) A string variable for the elapsed time.

        remain_var:
            (ttk.StringVar) A string variable for the remaining time.

        remaining_time_label:
            (ttk.Label) A label widget for the remaining time.

        elapsed_time_label:
            (ttk.Label) A label widget for the elapsed time.

        playback_slider:
            (ttk.Scale) A slider widget for controlling the playback.

        current_timestamp:
            (int) The current timestamp.

        skipped:
            (int) A flag that indicates whether the movie has been skipped or not.

    """

    def __init__(self, master, main_window):
        """ This method initializes the movie player window. """

        # Call the parent class constructor.
        super().__init__(master, main_window)

        # A flag that indicates whether the controls are visible or not
        self.fullscreen_button = None
        self.stop_button = None
        self.controls_visible = True
        # A flag that indicates whether the window is in full-screen mode or not
        self.fullscreen = False

        # A button widget for toggling full-screen mode
        self.play_pause_button = None
        # A flag that indicates whether the movie has started playing or not
        self.movie_started = False

        # A slider widget for controlling the volume
        self.volume_slider = None
        # A button widget for toggling mute mode
        self.volume_mute_toggle_button = None

        # A thread that is used to update the elapsed/remaining time labels
        self.time_update_thread = None
        # An event that is used to signal thread termination
        self.stop_movie_event = threading.Event()  # Create an event to signal thread termination

        # A frame widget for movie playback
        self.movie_player_frame = None
        # A VLC instance
        self.instance = None
        # A VLC media object
        self.media = None
        # A VLC media player object
        self.player = None

        # A frame widget for movie playback controls
        self.playback_controls_frame = None

        # A label widget for the greeting message
        self.movie_player_greeting_label = None
        # A string variable for the elapsed time
        self.elapsed_var = ttk.StringVar(value="00:00:00")
        # A string variable for the remaining time
        self.remain_var = ttk.StringVar(value="00:00:00")
        # A label widget for the remaining time
        self.remaining_time_label = None
        # A label widget for the elapsed time
        self.elapsed_time_label = None
        # A slider widget for controlling the playback
        self.playback_slider = None  # Store a reference to the playback slider
        # The current timestamp
        self.current_timestamp = 0  # Store the current timestamp
        # A flag that indicates whether the movie has been skipped or not
        self.skipped = 0  # flag: 0 = not skipped, 1 = skipped

        # Create a frame widget for movie playback
        self.movie_player_frame = ttk.Frame(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.movie_player_frame.pack(fill=ttk.BOTH, expand=True, pady=1)

        # Bind the resize event to a method
        self.movie_player_frame.bind("<Configure>", self.on_window_resize)

        # Create a frame widget for movie playback controls
        self.playback_controls_frame = ttk.Frame(self)
        self.playback_controls_frame.pack(fill=ttk.BOTH, expand=True)

        # Create a VLC instance.
        self.instance = vlc.Instance()

        # Create a VLC media player object.
        self.player = self.instance.media_player_new()

        # Force a refresh of the window.
        self.movie_player_frame.update()

    def start_movie_player(self):
        """ This method starts the movie player.
        It is called when the user clicks the 'Play Movie' button in the selected movie window. """
        # Increase the streaming requests counter
        client.increase_streaming_requests_counter()
        # Get the RTP URL for the movie
        rtp_url = client.get_movie_rtp_url()

        # Attach the media player to the frame
        self.player.set_hwnd(self.movie_player_frame.winfo_id())
        # Load the media file into the VLC media player object
        self.media = self.instance.media_new(rtp_url)
        # Get the media resource locator (MRL)
        self.media.get_mrl()
        # Set the media to be played by the media player
        self.player.set_media(self.media)
        # Maximize the window
        self.master.state('zoomed')
        # Create media playback controls.
        self.create_controls()

        # Start the time update thread.
        self.start_time_update_thread()

        # Create a style for the movie player greeting label.
        movie_player_greeting_style = ttk.Style()
        movie_player_greeting_style.configure("movie_player_greeting_style.Light.TLabel", font="Consolas 21")

        # Create a label widget for the greeting message.
        self.movie_player_greeting_label = ttk.Label(
            self.movie_player_frame,
            text=f"IT'S MOVIE TIME! {emoji.emojize(':film_frames:')} \n\n"
                 f"Click the {emoji.emojize(':play_button:')} button to start playing the movie.\n\n"
                 f"Don't forget    {emoji.emojize(':popcorn:')}    {emoji.emojize(':cup_with_straw:')}    {emoji.emojize(':vibration_mode:')}\n\n"
                 f"Enjoy!    {emoji.emojize(':star-struck:')}",
            bootstyle=LIGHT,
            style="movie_player_greeting_style.Light.TLabel"
        )
        self.movie_player_greeting_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def create_controls(self):
        """ This method creates the playback controls.
        The controls are created in a separate frame widget than that of the movie itself,
        and is placed at the bottom of the movie player window.
        The controls include buttons for playing/pausing/stopping the movie,
        toggling full-screen mode, and sliders for controlling the volume/playback. """

        # Create a style for the icons that are small sized.
        style_for_the_small_icons = ttk.Style()
        style_for_the_small_icons.configure("style_for_the_small_icons.Link.TButton", font="Consolas 21")

        # Create a style for the icons that are medium sized.
        style_for_the_medium_icons = ttk.Style()
        style_for_the_medium_icons.configure("style_for_the_medium_icons.Link.TButton", font="Consolas 16")

        # Create a style for the icons that are big sized.
        style_for_the_big_icons = ttk.Style()
        style_for_the_big_icons.configure("style_for_the_big_icons.Link.TButton", font="Consolas 14")

        # background="#2B3E50"

        # Create a button widget for stopping the movie.
        self.stop_button = ttk.Button(
            self.playback_controls_frame,
            text=emoji.emojize(":stop_button:"),
            cursor="hand2",
            bootstyle="Link",
            style="style_for_the_big_icons.Link.TButton",
            command=lambda: self.stop_movie()
        )
        self.stop_button.pack(side=LEFT, fill=X)

        # Create a button widget for playing/pausing the movie.
        self.play_pause_button = ttk.Button(
            self.playback_controls_frame,
            text=emoji.emojize(":play_button:"),
            cursor="hand2",
            bootstyle="Link",
            style="style_for_the_big_icons.Link.TButton",
            command=lambda: self.play_pause_movie()
        )
        self.play_pause_button.pack(side=LEFT, fill=X)

        # Create a button widget for toggling full-screen mode.
        self.fullscreen_button = ttk.Button(
            self.playback_controls_frame,
            text=emoji.emojize(":window:"),
            bootstyle="link",
            style="style_for_the_medium_icons.Link.TButton",
            cursor="hand2",
            command=lambda: self.toggle_fullscreen(False)
        )
        self.fullscreen_button.pack(side=LEFT, fill=X)

        # Bind the 'c' key press event to the toggle_controls method
        self.master.bind('c', self.toggle_controls)
        # Set the elapsed time to 00:00:00
        self.elapsed_var = StringVar(value="00:00:00")
        # Create a label widget for the elapsed time.
        self.elapsed_time_label = ttk.Label(self.playback_controls_frame, textvariable=self.elapsed_var,
                                            font="Consolas 12")
        self.elapsed_time_label.pack(side=tk.LEFT, padx=10)

        # Create a slider widget for controlling the playback.
        self.playback_slider = ttk.Scale(
            self.playback_controls_frame,
            from_=0,
            to=client.get_selected_movie_length_in_seconds_as_integer(),
            cursor="hand2"
        )
        self.playback_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Bind the slider release event to a method.
        self.playback_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # Set the initial position of the slider to 0
        self.playback_slider.set(0)

        self.remain_var = StringVar(value=format_time(client.get_selected_movie_length_in_seconds_as_integer()))

        # Create a label widget for the remaining time.
        self.remaining_time_label = ttk.Label(self.playback_controls_frame, textvariable=self.remain_var,
                                              font="Consolas 12")
        self.remaining_time_label.pack(side=tk.LEFT, padx=10)

        # Create a button widget for toggling mute.
        self.volume_mute_toggle_button = ttk.Button(
            self.playback_controls_frame,
            text=emoji.emojize(":speaker_medium_volume:"),
            cursor="hand2",
            bootstyle="Link",
            style="style_for_the_small_icons.Link.TButton",
            command=lambda: self.toggle_mute()
        )
        self.volume_mute_toggle_button.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Create a slider widget for controlling the volume.
        self.volume_slider = ttk.Scale(
            self.playback_controls_frame,
            from_=0,
            to=100,
            length=200,
            command=self.set_volume,
            cursor="hand2"
        )
        self.volume_slider.pack(side=tk.LEFT, padx=10)

        # Set the initial position of the slider to 50, meaning set the initial volume to 50%.
        self.volume_slider.set(50)

    def toggle_fullscreen(self, movie_ended_while_fullscreen_is_on):
        """ This method toggles the fullscreen mode.
        It is called when the user clicks the fullscreen button or when the movie ends while fullscreen is on.

            Parameter:
                movie_ended_while_fullscreen_is_on:
                    (bool) A flag that indicates whether the movie ended while fullscreen is on or not.
        """

        # Toggle the fullscreen flag.
        self.fullscreen = not self.fullscreen

        # Set the fullscreen mode attribute of the window accordingly.
        self.master.attributes("-fullscreen", self.fullscreen)

        # Check if the movie ended while fullscreen is on.
        if not movie_ended_while_fullscreen_is_on:
            # Update the visibility of the playback controls.
            self.toggle_controls(event=None)

    def toggle_controls(self, event):
        """ This method updates the visibility of the playback controls.
        It is called when the user toggles fullscreen mode or when the mouse leaves the window.
        It is also called when the user clicks the fullscreen button. """

        # Check the fullscreen flag.
        if self.fullscreen:
            # Check the controls a visibility flag.
            if self.controls_visible:
                # Hide the playback controls.
                self.playback_controls_frame.pack_forget()
                self.controls_visible = False
            else:
                # Show the playback controls.
                self.playback_controls_frame.pack(fill=ttk.BOTH, expand=True)
                self.controls_visible = True

    def toggle_mute(self):
        """ This method toggles the mute mode.
        It is called when the user clicks the mute button. """
        # Check if the volume is greater than 0.
        if self.player.audio_get_volume() > 0:
            # Set the volume to 0.
            self.set_volume(0)
            # Set the volume slider position to 0.
            self.volume_slider.set(0)
        else:
            # Set the volume to 50.
            self.set_volume(50)
            # Set the volume slider position to 50.
            self.volume_slider.set(50)

    def start_time_update_thread(self):
        """ This method starts the time update thread.
        The time update thread is used to update the elapsed/remaining time labels as well as the slider position. """

        # Clear the stop movie event
        self.stop_movie_event.clear()
        # Create and start a new thread for time updates
        self.time_update_thread = threading.Thread(target=self.update_time_labels_thread)
        self.time_update_thread.daemon = True
        self.time_update_thread.start()

    def update_time_labels_thread(self):
        """ This method updates every second the elapsed/remaining time labels as well as the slider position. """

        # As long as the movie is playing, update the labels every second
        while not self.stop_movie_event.is_set():
            self.update_time_labels()
            time.sleep(1)

    def update_time_labels(self):
        """ This method updates the elapsed/remaining time labels as well as the slider position.
        It is called every second by the time update thread. """

        # Check if the movie has ended.
        if (self.player.get_state() == vlc.State.Ended or
                client.get_selected_movie_length_in_seconds_as_integer() <= self.current_timestamp):
            self.elapsed_var.set(client.get_selected_movie_data()['length_hhmmss_string'])
            self.remain_var.set("00:00:00")
            self.stop_movie()

        # Check if the movie is not playing but also not ended.
        if (self.player.get_state() == vlc.State.Paused
                or self.player.get_state() == vlc.State.Stopped
                or self.player.get_state() == vlc.State.Opening
                or self.player.get_state() == vlc.State.NothingSpecial
                or self.player.get_state() == vlc.State.Buffering):
            return

        # Check if the movie is not playing.
        if self.player.get_state() != vlc.State.Playing:
            return

        # Update the current timestamp by adding 1 second.
        self.current_timestamp += 1

        # Get the movie length in seconds from the client object.
        movie_length_in_seconds = client.get_selected_movie_length_in_seconds_as_integer()

        # Calculate elapsed time.
        elapsed_time = min(movie_length_in_seconds, self.current_timestamp)
        elapsed_time_str = format_time(elapsed_time)

        # Calculate remaining time.
        remaining_time = max(movie_length_in_seconds - self.current_timestamp, 0)
        remaining_time_str = format_time(remaining_time)

        # Update the elapsed time label
        self.elapsed_var.set(elapsed_time_str)

        # Update the remaining time label
        self.remain_var.set(remaining_time_str)

        # Update the slider position
        self.playback_slider.set(self.current_timestamp)

    def stop_movie(self):

        # Set the event to signal the time update thread to stop
        self.stop_movie_event.set()

        # Reset the current timestamp
        self.current_timestamp = 0

        # Reset the movie start flag
        self.movie_started = False

        # Stop the movie from playing in client side
        self.player.stop()

        # Stop the movie from streaming in server side
        client.stop_streaming_movie()

        # Destroy all widgets in the playback controls frame
        for widget in self.playback_controls_frame.winfo_children():
            widget.destroy()

        # Toggle fullscreen off
        if self.fullscreen:
            self.toggle_fullscreen(True)

        # Restore the window to the normal state.
        self.master.state('normal')

        # Restore the window to the previous size and position it to the center of the screen.
        center_window(self, 800, 600)

        # Switch back to the movie gallery window
        self.main_window.switch_windows(MOVIE_GALLERY_WINDOW)

    def on_slider_release(self, event):
        """ This method handles the playback slider release event.
        It is called when the user releases the playback slider after dragging it.
        It sends a skip request to the server to skip to the time of the playback slider's value.

            Parameter:
                    event:
                        (tkinter.Event) The event object.
        """

        # set the current timestamp to the slider's value
        self.current_timestamp = int(float(self.playback_slider.get()))
        # set the flag to 1 to indicate that a skip request was sent
        self.skipped = 1

        # Calculate the hours, minutes, and seconds
        hours = int(self.current_timestamp // 3600)
        minutes = int((self.current_timestamp % 3600) // 60)
        seconds = int(self.current_timestamp % 60)

        # Send a skip request to the server
        client.skip_to_timestamp(hours, minutes, seconds)

    def set_volume(self, value):
        """ This method sets the volume of the movie.
        It is called when the user changes the volume slider position.
        It is also called when the user clicks the mute button.

        Parameter:
                  value:
                       (str) Representing the volume percentage. For example, '50.0' means 50%.
        """
        # Get the value from the volume slider.
        volume = int(float(value))

        # Set the volume of the movie to the value of the volume slider.
        self.player.audio_set_volume(volume)

        # Change the volume/mute button icon and style according to the volume.
        if volume == 0:
            self.volume_mute_toggle_button.config(text=emoji.emojize(":muted_speaker:"))
            self.volume_mute_toggle_button.config(style="style_for_the_medium_icons.Link.TButton")
        elif 0 < volume <= 33:
            self.volume_mute_toggle_button.config(text=emoji.emojize(":speaker_low_volume:"))
            self.volume_mute_toggle_button.config(style="style_for_the_medium_icons.Link.TButton")
        elif 33 < volume <= 66:
            self.volume_mute_toggle_button.config(text=emoji.emojize(":speaker_medium_volume:"))
            self.volume_mute_toggle_button.config(style="style_for_the_medium_icons.Link.TButton")
        elif volume > 66:
            self.volume_mute_toggle_button.config(text=emoji.emojize(":speaker_high_volume:"))
            self.volume_mute_toggle_button.config(style="style_for_the_medium_icons.Link.TButton")

    def on_window_resize(self, event):
        """ This method handles the resize of the movie player window,
        and bounds to the resize event of the movie_player_frame.
        It resizes the movie player frame, the playback controls frame to match the window size.
        To prevent the frames from overlapping when fullscreen mode is on,
        the playback controls frame height is resized to 1 pixel,
        and the movie player frame height is resized to the window height - 1 pixel.

            Parameter:
                    event:
                        (tkinter.Event) The event object.

        """

        # Get the window size from the event.
        width = event.width
        height = event.height

        # Update the movie player frame size to match the window size.
        self.movie_player_frame.config(width=width, height=height - 1)

        # Update the playback control frame size to match the window size.
        self.playback_controls_frame.config(width=width, height=1)

    def play_pause_movie(self):
        """ This method plays or pauses the movie.
        It is called when the user clicks the play/pause button. """

        # Check if the movie has not started
        if not self.movie_started:
            # Set the movie_started flag to True.
            self.movie_started = True
            # Hide the movie player greeting label.
            self.movie_player_greeting_label.place_forget()
            # Call the client method to start streaming the movie from the server.
            client.start_streaming_movie()
            # Wait for 1 second independently of the number of streaming requests
            time.sleep(1)
            # Start the playback at the client side.
            self.player.play()
            # Update the play/pause button icon.
            self.play_pause_button.config(text=emoji.emojize(":pause_button:"))
            return
        # The Movie has started, so toggle the pause/play state.
        self.player.pause()
        # Update the play/pause button icon.
        if self.play_pause_button.cget("text") == emoji.emojize(":play_button:"):
            self.play_pause_button.config(text=emoji.emojize(":pause_button:"))
        else:
            self.play_pause_button.config(text=emoji.emojize(":play_button:"))


class InformationWindow(BaseWindow):
    """ This class represents an information window that provides details about the VOD movie streaming project.
    It includes a brief project description and a "Project Portfolio" button for downloading more information.
    Users can return to the movie gallery from this window.

    Instance Attributes:

        information_label_frame:
            (ttk.LabelFrame) A label frame widget for the information.

        information_label:
            (ttk.Label) A label widget for the information.

        download_project_portfolio_button:
            (ttk.Button) A button widget for downloading the project portfolio.

        return_button:
            (ttk.Button) A button widget for returning to the movie gallery.

    """

    def __init__(self, master, main_window):
        """ This method initializes the information window. """
        # Call the constructor of the parent class.
        super().__init__(master, main_window)

        # Create a style for the icons that are small sized.
        download_project_portfolio_button_style = ttk.Style()
        download_project_portfolio_button_style.configure("download_project_portfolio_button_style.Link.TButton",
                                                          font="Consolas 14", justify="center")

        # Create a style for the icons that are medium sized.
        back_button_style = ttk.Style()
        back_button_style.configure("back_button_style.Link.TButton", font="Consolas 21")

        # Create a label frame widget for the information.
        self.information_label_frame = ttk.LabelFrame(self, text=" Information ")
        self.information_label_frame.pack(padx=20, pady=20, fill=ttk.BOTH, expand=True)

        # Create a label widget for the information.
        self.information_label = ttk.Label(
            self.information_label_frame,
            text="Welcome to VOD Movie streaming project by Kfir Sibirsky.\n"
                 "This app developed by me as part of the final project in the WORKSHOP: \n"
                 "COMPUTER COMMUNICATION (20588) course as part of my Computer Science\n"
                 "studies at THE OPEN UNIVERSITY OF ISRAEL.\n"
                 "The app is a client-server application that allows users to stream\n"
                 "movies from the movie server. It does so using 'python-vlc' which\n"
                 "is a VLC libray python binding for desktop platforms.\n"
                 "Taking user experience into consideration, the app is equipped with\n"
                 "a clean, intuitive and user-friendly interface. The media player\n"
                 "offer the user an array of control features including play, pause\n"
                 "stop, volume adjustment, jump to a specific point in time and a\n"
                 "fullscreen mode that automatically hides the playback controls.\n"
        )
        self.information_label.pack(padx=20, pady=5, fill=ttk.X, expand=True)

        # Create a button widget for downloading the project portfolio.
        download_icon = ImageTk.PhotoImage(
            Image.open("C:/Users/skfir/PycharmProjects/pythonProject5/assets/WordLogo.png"))
        self.download_project_portfolio_button = ttk.Button(
            self.information_label_frame,
            image=download_icon,
            cursor="hand2",
            text='Download Project Portfolio',
            bootstyle="Link",
            style="download_project_portfolio_button_style.Link.TButton",
            compound='top',
            command=client.download_project_portfolio
        )
        self.download_project_portfolio_button.image = download_icon  # Store a reference to avoid garbage collection
        self.download_project_portfolio_button.pack(padx=15, pady=5, fill=ttk.BOTH, expand=True)

        # Create a button widget for returning to the movie gallery.
        self.back_button = ttk.Button(
            self,
            text=emoji.emojize(":BACK_arrow:"),
            command=lambda: main_window.switch_windows(MOVIE_GALLERY_WINDOW),
            cursor="hand2",
            bootstyle="Link",
            style="back_button_style.Link.TButton"
        )
        self.back_button.pack(padx=15, pady=5, fill=ttk.BOTH, expand=True)


def center_window(self, width, height):
    """ This method centers a window on the screen.

        Parameters:
            self:
                (tkinter.Tk) The window to center.
            width:
                (int) The width of the window.
            height:
                (int) The height of the window.
    """

    # Get the screen width and height
    screen_width = self.master.winfo_screenwidth()
    screen_height = self.master.winfo_screenheight()

    # Calculate the x and y coordinates to center the window
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set the window size and position
    self.master.geometry(f"{width}x{height}+{x}+{y}")


########################################################################################################################
#                         The following part handles initialization of the client application.                         #
########################################################################################################################


def main():
    """ The main method. """
    # Connect the client to the server
    client.connect_client_to_server()

    # Get the movies from the server
    client.get_movies_from_server()

    # Register the exit handler
    atexit.register(client.notify_server_on_exit)

    # creates an instance of the ttk.Window class, which is used for theming.
    root = ttk.Window(themename="superhero")

    # The MainWindow class is instantiated.
    main_window_to_export = MainWindow(root)

    # starts the GUI application.
    root.mainloop()


if __name__ == "__main__":
    main()
