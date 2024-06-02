import importlib
import subprocess
import sys
import os


def check_and_install_package(package_name):
    """ Check if the package is installed. If not, install it. """

    try:
        importlib.import_module(package_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} is not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", package_name])
        print(f"{package_name} has been installed.")


def run_script(script_name):
    """ Run a python script. """
    subprocess.run([sys.executable, script_name])


if __name__ == '__main__':

    # Only install the packages if they aren't already installed
    required_packages = ["python-vlc", "Flask", "Flask-SQLAlchemy"]
    for package in required_packages:
        check_and_install_package(package)

    # Only run the database script if the database doesn't exist
    if not os.path.exists('./instance/movies_database.db'):
        # Run the database script
        run_script('database.py')

    # Run the server script
    run_script('server.py')
