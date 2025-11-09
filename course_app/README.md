# Learnit - Your Offline Learning Companion

Learnit is a modern, offline-first desktop application designed for focused learning. It transforms a structured folder of markdown files into an interactive course, complete with progress tracking, timers, and gamification to keep you motivated. Inspired by leading online learning platforms, Learnit brings the best of their features to a fully offline environment, ensuring you can learn anytime, anywhere, without distractions.

## Features

- **Modern UI/UX:** A clean, intuitive interface with a sidebar for easy navigation through course phases, modules, and topics.
- **Offline First:** No internet connection required. All your learning data is stored locally.
- **Course Upload:** Simply select a folder of markdown files, and Learnit will automatically parse and structure it into a course.
- **Markdown Rendering:** Course content is beautifully rendered with support for headers, lists, code blocks, and syntax highlighting.
- **Progress Tracking:** Your progress is automatically saved, so you can always pick up where you left off.
- **Gamification:**
    - **Points System:** Earn points for completing topics and hitting milestones.
    - **Badges:** Unlock badges for achievements like completing your first module or maintaining a learning streak.
- **Learning Timer:** Use the built-in timer to focus your study sessions and track time spent on each topic.
- **One-Click Setup:** A simple `setup_run.py` script handles everything from creating a virtual environment to installing dependencies and launching the app.

*(Screenshot of the main application window with the sidebar and a course topic displayed should be placed here.)*

## Installation

Getting started with Learnit is as simple as running a single command.

1.  **Prerequisites:**
    *   Python 3.8 or higher.
    *   `git` for cloning the repository.

2.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd learnit-app
    ```

3.  **Run the Setup Script:**
    The `setup_run.py` script will automatically:
    - Check your Python version.
    - Create a virtual environment.
    - Install all required dependencies.
    - Initialize the local database.
    - Launch the application for you.

    ```bash
    python course_app/setup_run.py
    ```

That's it! The application will launch, and you'll be ready to start learning.

## Usage Guide

1.  **First Launch:** On your first launch, Learnit will automatically load a sample course to get you started.
2.  **Uploading a Course:**
    -   *(This feature will be fully implemented in a future version. For now, you can add new courses by placing them in the `course_app` directory and re-running the application.)*
3.  **Navigating the Course:**
    -   Use the sidebar on the left to expand phases and modules and select a topic.
    -   The content of the selected topic will be displayed in the main area.
4.  **Learning with the Timer:**
    -   *(The timer UI will be added in a future version.)*
5.  **Tracking Your Progress:**
    -   *(The dashboard with detailed progress and rewards will be added in a future version.)*

*(A screenshot or GIF demonstrating the process of navigating the course sidebar should be placed here.)*

## Troubleshooting

-   **`ModuleNotFoundError: No module named 'PyQt6'`**:
    This error means the application is not running within its virtual environment. Make sure you are activating the virtual environment before running the app, or use the `run.sh`/`run.bat` scripts that will be provided in a future update. The `setup_run.py` script handles this for you on the first run.

-   **Qt Platform Plugin Errors on Linux (`xcb`)**:
    If you see errors related to the "xcb" plugin, it means some system-level dependencies are missing. The `setup_run.py` script attempts to guide you, but you may need to install them manually. For Debian/Ubuntu, you can run:
    ```bash
    sudo apt-get update && sudo apt-get install -y libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xfixes0 libxcb-xkb1 libxcb-cursor0
    ```
