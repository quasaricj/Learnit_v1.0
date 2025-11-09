import sys
import subprocess
import os
import venv
import shutil

VENV_DIR = "venv"
REQUIREMENTS_FILE = "requirements.txt"
DATABASE_FILE = "data/course_app.db"

def check_python_version():
    """Checks if the Python version is 3.8+."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"You are using Python {sys.version.split(' ')[0]}.")
        sys.exit(1)
    print("Python version check passed.")

def get_pip_path():
    """Gets the path to the pip executable in the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "pip")

def create_virtual_environment():
    """Creates a virtual environment if it doesn't exist or is incomplete."""
    pip_path = get_pip_path()
    if not os.path.exists(pip_path):
        print(f"Virtual environment is missing or incomplete. Creating in '{VENV_DIR}'...")
        if os.path.exists(VENV_DIR):
            shutil.rmtree(VENV_DIR)
        try:
            venv.create(VENV_DIR, with_pip=True)
            print("Virtual environment created successfully.")
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print("Virtual environment already exists and is complete.")


def install_dependencies():
    """Installs dependencies from requirements.txt."""
    pip_path = get_pip_path()
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([pip_path, "install", "-r", REQUIREMENTS_FILE])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: '{REQUIREMENTS_FILE}' not found.")
        sys.exit(1)

def initialize_database():
    """Initializes the SQLite database."""
    print("Initializing database...")
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(DATABASE_FILE):
        print("Database file not found. (This will be created by the app)")

    print("Database initialization check complete.")

def launch_application():
    """Launches the main application."""
    python_path = os.path.join(VENV_DIR, "bin", "python")
    if sys.platform == "win32":
        python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")

    print("Launching the Learnit application...")
    try:
        subprocess.run([python_path, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'main.py' not found.")
        sys.exit(1)

def main():
    """Main function to run the setup and launch the application."""
    print("--- Welcome to the Learnit Setup Script ---")
    check_python_version()
    create_virtual_environment()
    install_dependencies()
    initialize_database()

    print("\n--- Setup Complete ---")

    launch_application()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
