# ⚡ Habitify — Responsive Habit Tracking & Analytics Web App

Habitify is a habit-tracking web application engineered with a **dark charcoal / obsidian visual identity**, **purple activity heatmap & completion accents**, **muted gold statistics panels**, and a **fun, slightly savage motivational personality**.

---

## 🌟 Visual Identity & Key Highlights

- **Dark Charcoal / Black Canvas**: Deep `#0b0c10` and `#14151f` card surfaces with subtle frosted borders.
- **Muted Gold Statistics Panels**:
  - 🏆 **Total Completed Repetitions**: Lifetime habit tally with weekly momentum.
  - 🔥 **Current Streak**: Active unbroken chain of days with motivational tier badges.
  - 👑 **Longest Streak**: Historical record of unbroken discipline.
  - 🎯 **Monthly & Weekly Consistency**: Dynamic completion percentages.
- **Interactive Monthly Habit Tracker Grid**:
  - Habit rows with category badges, streak counters, and quick actions (edit/delete).
  - Date columns (1 to 31) with weekday initials (M, T, W, T, F, S, S).
  - **"Today" Glowing Column**: Real-time highlight of current calendar day.
  - **Purple Glow Completions**: Clickable interactive check pills with purple accents (`#8b5cf6`).
  - **Protected Future Dates**: Prevents accidental future completion with friendly alerts.
  - **Purple Activity Heatmap**: Bottom row tracking daily completion volume across 4 purple intensity shades.
- **Lower Dashboard Sections**:
  - 🏆 **Discipline Leaderboard**: Ranked community standings with podium medals and streak points.
  - ⚡ **Activity Stream**: Live chronological feed of completed habits and earned discipline XP.
- **Scrollable In-Depth Analytics Section (Chart.js)**:
  - 📊 **Weekly Progress Chart**: Monday–Sunday completion bar chart with top-performing day badge.
  - 📈 **Monthly Trend Line Chart**: 30-day smooth bezier curve with purple gradient fill.
  - ⚖️ **Habit Comparison Chart**: Direct consistency benchmark across Gym, Studying, Reading, etc.
  - 🍩 **Category Balance Doughnut**: Visual breakdown across Fitness, Learning, Health, and Mind.
- **Savage & Hype Personality Engine**:
  - Hype toasts when habits are crushed: *"THAT'S WHAT I'M TALKING ABOUT!"*, *"Congratulations! You're moving closer to your next version."*
  - Savage toasts when habits are missed on past days: *"HAHAHA, really thought you would go all in this time?"*, *"Guess you don't want it bad enough."*
  - **Milestone Confetti**: Canvas-confetti bursts for 3-day, 7-day, 14-day, 21-day, and 30-day streaks.
  - **Audio FX Synthesizer**: Built-in Web Audio API chimes (toggleable on/off).
- **Progressive Web App (PWA)**: Installable on Windows, macOS, Android, and iOS home screens.

---

## 📁 Project Architecture

```
habitify/
│── app.py                  # Flask server with RESTful APIs, Auth & Session logic
│── database.py             # Database abstraction layer (SQLite default + Supabase ready)
│── models.py               # Streak calculation algorithms, stats, and savage quote engine
│── requirements.txt        # Python dependencies (Flask, Werkzeug, Pillow)
│── run.bat                 # 1-Click Windows launch script
│── test_app.py             # Automated 10-point test suite
│── .env.example            # Environment variables template
│── README.md               # Complete documentation & deployment guide
│
├── static/
│   ├── css/
│   │   ├── style.css       # Dark charcoal theme, typography, grid, responsive rules
│   │   └── animations.css  # Toasts, confetti glows, checkbox pop transitions
│   ├── js/
│   │   ├── api.js          # REST API client connecting frontend to Flask backend
│   │   ├── notifications.js# Savage/Hype toasts, Web Audio synth, milestone confetti
│   │   ├── analytics.js    # Chart.js initialization and reactive updates
│   │   └── app.js          # Main UI controller, matrix table renderer, habit CRUD
│   ├── icons/
│   │   ├── icon-192.png    # PWA launcher icon (192x192)
│   │   └── icon-512.png    # PWA high-res icon (512x512)
│   ├── manifest.json       # PWA Web App Manifest
│   └── sw.js               # Service Worker for PWA caching & offline resilience
│
└── templates/
    └── index.html          # Main single-page application template
```

---

## 🚀 How to Run on Your Windows Laptop using VS Code

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File > Open Folder...**
3. Navigate to:
   ```
   C:\Users\riddhi yadav\.gemini\antigravity\scratch\habitify
   ```
4. Click **Select Folder**.

### Step 2: Open the Integrated Terminal
- Press **Ctrl + `** (backtick) or select **Terminal > New Terminal** from the top menu.

### Step 3: Install Required Dependencies
Run the following command in the terminal:
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
You can start the server in either of two ways:

**Option A (Terminal):**
```powershell
python app.py
```

**Option B (1-Click Shortcut):**
- Double-click `run.bat` in File Explorer or run `.\run.bat` in PowerShell.

### Step 5: Open in Your Browser
- Open your browser (Chrome, Edge, Brave, or Firefox) and navigate to:
  ```
  http://localhost:5000
  ```
- You will immediately see Habitify loaded with **Alex Morgan's pre-seeded active account** (with 7 default habits, 30 days of history, live streaks, activity logs, and vibrant charts).

---

## 🧪 Testing Features & Workflows

### 1. 1-Click Habit Completion & Savage Alerts
- Click any empty box on today's column (highlighted in purple) to mark a habit complete.
- Hear the audio chime, see the checkbox burst in electric purple, and receive an instant hype toast!
- Notice how the **Total Completed**, **Current Streak**, and **Heatmap** row update immediately with zero page refresh.

### 2. Creating, Editing & Deleting Habits
- Click **"+ New Habit"** in the top action bar.
- Choose a name (e.g. *Cold Shower*), pick a category (*Health*), enter an icon (*🚿*), choose a target (*7 days/wk*), and click **Save**.
- To edit, click the **pencil icon** on any habit row.
- To delete, click the **trash can icon** and confirm.

### 3. Month Navigation
- Use the `<` and `>` arrows at the top of the tracker to browse past and upcoming months.
- Click the **"Today"** button to instantly jump back to the current month and auto-scroll to today's date.

### 4. Daily Summary & Weekly Review Modal
- Click **"Daily Summary"** (top right) or **"Weekly Review"** (sidebar).
- The Savage AI review evaluates your actual weekly percentage:
  - If $\ge 85\%$: Hype commentary celebrating your discipline.
  - If $< 60\%$: Savage critique motivating you to stop making excuses.

### 5. Testing the Automated Test Suite
Run the included 10-point test suite anytime:
```powershell
python test_app.py
```

---

## 📱 Responsive Testing & PWA Installation

### Responsive Testing (Laptop vs Mobile):
1. In Google Chrome or Microsoft Edge, press **F12** to open Developer Tools.
2. Click the **Toggle device toolbar** button (or press `Ctrl + Shift + M`).
3. Select **iPhone 14 Pro**, **Pixel 7**, or **iPad Mini**.
4. Observe:
   - The desktop sidebar collapses into a smooth mobile drawer accessible via the hamburger icon (`☰`).
   - The habit tracker matrix table scrolls horizontally while keeping the **Habit Names column pinned to the left** so you never lose context.
   - All tap targets are comfortably sized ($\ge 34\text{px}$).
   - Charts dynamically adapt their dimensions.

### Installing as a Mobile / Desktop PWA:
- **On Desktop (Chrome/Edge)**: Look at the right side of the browser address bar for the **Install Habitify** icon (a monitor with a down arrow). Click **Install** to run Habitify in its own standalone app window!
- **On Android (Chrome)**: Tap the three dots menu > **Add to Home screen** > **Install**.
- **On iOS (Safari)**: Tap the Share button > **Add to Home Screen**.

---

## ☁️ Cloud Synchronization & Supabase Migration

Habitify is built with a decoupled architecture. While it uses local SQLite (`habitify.db`) out of the box for zero-setup local development, switching to **Supabase (PostgreSQL)** is straightforward:

### Step 1: Create a Free Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a free account.
2. Click **New Project** and name it `habitify-db`.
3. Note your project URL and API keys in **Project Settings > API**.

### Step 2: Run the SQL Schema in Supabase SQL Editor
In your Supabase dashboard, open the **SQL Editor** and execute:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    avatar TEXT DEFAULT '⚡',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habits table
CREATE TABLE IF NOT EXISTS habits (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    color TEXT DEFAULT '#8b5cf6',
    icon TEXT DEFAULT '✨',
    target_days_per_week INT DEFAULT 7,
    daily_goal TEXT DEFAULT '1x daily',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active INT DEFAULT 1
);

-- Habit completion logs
CREATE TABLE IF NOT EXISTS habit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    habit_id BIGINT REFERENCES habits(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('completed', 'missed', 'skipped')),
    notes TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(habit_id, date)
);

-- Activity stream
CREATE TABLE IF NOT EXISTS activity_feed (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    habit_name TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Step 3: Connect Habitify to Supabase
Set the environment variables in your `.env` or system environment:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:yourpassword@db.yourproject.supabase.co:5432/postgres
```

---

## 🌐 Deploying Online (Access from Phone & Laptop)

To access Habitify anywhere from both your phone and laptop using the same account:

### Recommended: Deploy Free on Render.com or Railway
1. Push this folder to a GitHub repository.
2. Go to [render.com](https://render.com) and create a **New Web Service**.
3. Select your repository.
4. Set:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (or `python app.py`)
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: (any random 32-character string)
   - `SUPABASE_URL` & `SUPABASE_KEY` (if using cloud database)
6. Click **Deploy Web Service**. You will receive an `https://habitify.onrender.com` URL that you can open and install on both your phone and laptop!
