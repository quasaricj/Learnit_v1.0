# PyQt Offline Course Learning App(learnit) - Detailed Development Plan
App name is "Learnit"

## Project Overview

**Goal:** Build a modern, offline desktop learning application (similar to Coursera/Udemy/UpGrad) using PyQt that:
- Displays courses organized by phases, modules, and topics from markdown files
- Tracks progress and completion
- Gamifies learning with timers, points, badges, and rewards
- Works 100% offline with local data persistence

---

## 1. Research: Features of Modern Course Platforms

### Key Features from Coursera, Udemy, and UpGrad:

1. **Clean Dashboard/LMS Interface**
   - Modern sidebar navigation
   - Course catalog with thumbnails and descriptions
   - Search and filter functionality
   - Progress tracking and analytics

2. **Course Content Delivery**
   - Video lectures, documents, and text content
   - Structured curriculum (sections/modules/lessons)
   - Progress bars and completion indicators
   - Resume where you left off

3. **Interactive Learning**
   - Quizzes and assessments
   - Downloadable resources
   - Practice exercises
   - Completion certificates

4. **Progress Tracking**
   - Visual progress indicators
   - Time spent on courses
   - Completion percentages
   - Learning streaks

5. **Gamification Elements**
   - Points/XP system
   - Badges and achievements
   - Leaderboards (optional)
   - Daily streaks and milestones
   - Timed challenges with bonus rewards

---

## 2. App Features & Requirements

### Core Features:

#### A. Modern Course UI/UX
- **Sidebar Navigation:** Tree/list view showing:
  - Phases (e.g., Phase 1: Programming Fundamentals)
  - Modules (e.g., Module 1: Core Programming Concepts)
  - Topics (individual lessons/topics)
- **Main Content Panel:** Markdown renderer displaying course content
- **Dashboard:** Overview of user stats, progress, next lesson
- **Search/Filter:** Quick navigation to any topic
- **Responsive Layout:** Clean, modern design

#### B. Course Upload & Auto-Structure
- **Upload Functionality:** 
  - Select folder containing markdown course structure
  - Auto-parse folder hierarchy (Phase > Module > Topic)
  - Build navigable course tree automatically
- **Course Detection:**
  - Recognize numbered prefixes for ordering
  - Handle nested folder structures
  - Validate markdown files and detect empty files

#### C. Content Display & Learning
- **Markdown Rendering:**
  - Support for headers, lists, code blocks, images
  - Syntax highlighting for code
  - Checkboxes for exercises/checklists
- **Topic Timer:**
  - Configurable dedicated learning time per topic
  - Visual timer display (countdown)
  - Pause/resume functionality
- **Completion Tracking:**
  - Mark topics as complete
  - Save progress locally
  - Resume from last position

#### D. Gamification & Rewards System
- **Points/XP System:**
  - Award points on topic completion
  - Bonus points for completing within dedicated time
  - Bonus for daily streaks
- **Badges & Achievements:**
  - Unlock badges for milestones (complete phase, 7-day streak, etc.)
  - Visual badge collection/trophy room
- **Timer-Based Rewards:**
  - Set target time per topic
  - Extra points if completed before time expires
- **Progress Analytics:**
  - Total time spent learning
  - Topics completed today/this week
  - Current streak count
  - Points leaderboard (if multi-user on same device)

#### E. Offline-First Architecture
- **No Internet Required:** All functionality works offline
- **Local Data Storage:** SQLite database or JSON files for:
  - User profile and settings
  - Course structure and metadata
  - Progress and completion data
  - Points, badges, and achievements
  - Timer history and statistics
- **Export Functionality:**
  - Export progress report as PDF/Markdown
  - Backup/restore user data

---

## 3. Technical Architecture

### Technology Stack:
- **Framework:** PyQt5 or PyQt6
- **Markdown Rendering:** `markdown` library + QTextBrowser/QWebEngineView
- **Database:** SQLite3 (built-in with Python)
- **Additional Libraries:**
  - `qtawesome` - for modern icons
  - `markdown` - markdown to HTML conversion
  - `reportlab` or `weasyprint` - for PDF export (optional)

### App Structure:

```
course_app/
├── setup_run.py                 # One-click setup and run script
├── requirements.txt             # Python dependencies
├── main.py                      # Application entry point
├── ui/
│   ├── main_window.py          # Main application window
│   ├── dashboard.py            # Dashboard view
│   ├── course_viewer.py        # Course content display
│   ├── sidebar.py              # Navigation sidebar
│   ├── upload_dialog.py        # Course upload interface
│   ├── rewards_panel.py        # Points, badges, achievements
│   └── settings_dialog.py      # App settings
├── core/
│   ├── course_parser.py        # Parse markdown folder structure
│   ├── database.py             # SQLite database operations
│   ├── progress_tracker.py    # Track user progress
│   ├── timer_manager.py        # Timer functionality
│   └── rewards_engine.py       # Points/badge calculation
├── utils/
│   ├── markdown_renderer.py    # Render markdown to display
│   └── file_utils.py           # File operations
└── assets/
    ├── icons/                   # UI icons
    ├── badges/                  # Badge images
    └── styles.qss              # Application stylesheet
```

---

## 4. Detailed Feature Implementation Plan

### Phase 1: Setup & Core UI (Days 1-2)
- Create project structure
- Implement MainWindow with sidebar and central widget
- Design and implement Dashboard view
- Setup database schema for user data and progress

### Phase 2: Course Upload & Parsing (Days 3-4)
- Implement folder selection dialog
- Build course parser to read markdown folder structure
- Create course tree data model
- Populate sidebar navigation with parsed course structure
- Handle empty files and missing topics

### Phase 3: Content Display (Days 5-6)
- Implement markdown rendering in main content area
- Add code syntax highlighting
- Create topic navigation (previous/next)
- Implement "mark as complete" functionality
- Save and restore reading position

### Phase 4: Timer System (Days 7-8)
- Build timer widget with start/pause/reset
- Add configurable target time per topic
- Implement timer notifications
- Save timer history to database
- Display time spent on each topic

### Phase 5: Gamification & Rewards (Days 9-11)
- Implement points calculation system
- Create badge unlock logic and storage
- Design and build rewards panel UI
- Add achievement notifications
- Implement daily streak tracking
- Build progress analytics dashboard

### Phase 6: Polish & Features (Days 12-14)
- Add search/filter functionality
- Implement export progress feature
- Create settings panel (themes, timer defaults, etc.)
- Add tooltips and help
- Error handling and validation
- Performance optimization

### Phase 7: Testing & Setup Script (Days 15-16)
- Comprehensive testing of all features
- Create `setup_run.py` for one-click installation
- Write documentation
- Package application

---

## 5. Database Schema

### Tables:

#### users
- id (PRIMARY KEY)
- username
- created_at
- total_points
- current_streak
- longest_streak

#### courses
- id (PRIMARY KEY)
- name
- path
- uploaded_at

#### topics
- id (PRIMARY KEY)
- course_id (FOREIGN KEY)
- phase_name
- module_name
- topic_name
- file_path
- order_number
- target_time_minutes

#### progress
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- topic_id (FOREIGN KEY)
- completed
- completion_date
- time_spent_seconds
- bonus_earned

#### badges
- id (PRIMARY KEY)
- name
- description
- icon_path
- unlock_criteria

#### user_badges
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- badge_id (FOREIGN KEY)
- unlocked_at

---

## 6. Gamification Rules

### Points System:
- **Complete Topic:** 10 points
- **Complete Within Target Time:** +5 bonus points
- **Complete First Topic of Day:** +10 bonus points
- **Complete All Topics in Module:** +50 bonus points
- **Complete All Topics in Phase:** +200 bonus points
- **Maintain 7-Day Streak:** +100 bonus points

### Badges:
1. **First Step** - Complete your first topic
2. **Module Master** - Complete any module
3. **Phase Champion** - Complete any phase
4. **Speed Learner** - Complete 10 topics within target time
5. **Dedicated Student** - Maintain 7-day learning streak
6. **Time Master** - Complete 30 topics within target time
7. **Course Conqueror** - Complete entire course
8. **Streak Legend** - Maintain 30-day learning streak

---

## 7. User Experience Flow

### First Launch:
1. Welcome screen with app tutorial
2. Create user profile (username)
3. Upload first course (browse to markdown folder)
4. Course structure auto-parsed and displayed
5. Start learning from first topic

### Daily Usage:
1. Launch app → Dashboard shows:
   - Current streak
   - Today's progress
   - Next recommended topic
   - Recent achievements
2. Navigate to desired phase/module/topic
3. Set timer (optional) and start learning
4. Mark topic complete when finished
5. Receive points and potential badge unlocks
6. View progress and rewards in dashboard

---

## 8. Setup & Distribution

### One-Click Setup Script (setup_run.py):
The script will:
1. Check Python version (3.8+)
2. Create virtual environment automatically
3. Install all required dependencies
4. Initialize SQLite database with schema
5. Create necessary folders (assets, data, etc.)
6. Launch the application
7. Handle errors gracefully with user-friendly messages

### Usage:
```bash
python setup_run.py
```

No other commands or technical steps required.

---

## 9. Future Enhancements (Optional)

- Dark mode / custom themes
- Export course completion certificate
- In-app markdown editor for notes
- Pomodoro timer integration
- Multi-user profiles on same device
- Cloud sync (optional online feature)
- Quiz/assessment integration
- Voice-over support for content
- Mobile companion app

---

## 10. Success Criteria

- ✅ App runs completely offline
- ✅ Automatically parses markdown course folders
- ✅ Displays content in clean, modern UI
- ✅ Tracks progress and time spent
- ✅ Awards points and badges based on rules
- ✅ One-click setup with setup_run.py
- ✅ Handles empty/missing files gracefully
- ✅ Saves all data locally (no data loss)
- ✅ Intuitive and motivating user experience

---

## Conclusion

This plan provides a comprehensive roadmap for building a feature-rich, offline PyQt course learning application with gamification, progress tracking, and modern UX inspired by leading platforms like Coursera and Udemy. The app will be beginner-friendly to set up and use, while providing a powerful and motivating learning experience.