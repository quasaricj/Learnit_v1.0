import os

def get_data_dir():
    """Returns the path to the application's data directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
