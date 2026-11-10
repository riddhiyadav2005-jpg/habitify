"""
app.py - Flask backend server for Habitify Habit Tracker.
Provides RESTful APIs for authentication, habit management, monthly matrix tracking,
live streak calculations, analytics, and savage/hype motivational notifications.
"""

import os
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

import database
import models

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "habitify-super-secret-key-2026")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Initialize database tables on server start
with app.app_context():
    database.init_db()

def get_current_user_id():
    """Get the current user id from session or fallback to demo user (id=1)."""
    return session.get("user_id", 1)

# ==========================================
# PAGE ROUTES
# ==========================================

@app.route("/")
def index():
    """Serve the main Habitify responsive Single Page Application."""
    return render_template("index.html")

# ==========================================
# AUTHENTICATION APIS
# ==========================================

@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Return currently logged-in user profile."""
    user_id = session.get("user_id")
    if not user_id:
        # Default to demo user for smooth immediate experience
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, display_name, avatar FROM users WHERE id = 1")
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            return jsonify({"authenticated": True, "user": dict(user)})
        return jsonify({"authenticated": False, "user": None})

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, display_name, avatar FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"authenticated": True, "user": dict(user)})
    return jsonify({"authenticated": False, "user": None})

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user, seed default habits, and start session."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    display_name = data.get("display_name", username).strip()

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Username or email already exists"}), 400

    password_hash = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, display_name, avatar)
        VALUES (?, ?, ?, ?, '⚡')
    """, (username, email, password_hash, display_name or username))
    new_user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Seed default starter habits (Gym, Studying, Jogging, Reading, etc.)
    database.create_default_habits_for_user(new_user_id)

    session["user_id"] = new_user_id
    return jsonify({
        "success": True,
        "user": {
            "id": new_user_id,
            "username": username,
            "display_name": display_name or username,
            "avatar": "⚡"
        }
    })

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate existing user."""
    data = request.get_json() or {}
    username_or_email = data.get("username", "").strip()
    password = data.get("password", "")

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users 
        WHERE username = ? OR email = ?
    """, (username_or_email, username_or_email))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"],
            "avatar": user["avatar"]
        }
    })

@app.route("/api/auth/demo-login", methods=["POST"])
def demo_login():
    """1-Click instant login to demo account with realistic pre-populated data."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = 'demo_user' OR id = 1")
    demo_user = cursor.fetchone()
    conn.close()

    if demo_user:
        session["user_id"] = demo_user["id"]
        return jsonify({
            "success": True,
            "user": {
                "id": demo_user["id"],
                "username": demo_user["username"],
                "display_name": demo_user["display_name"],
                "avatar": demo_user["avatar"]
            }
        })
    return jsonify({"error": "Demo user not found"}), 404

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Log out current user."""
    session.clear()
    return jsonify({"success": True})

# ==========================================
# HABIT MANAGEMENT APIS
# ==========================================

@app.route("/api/habits", methods=["GET"])
def list_habits():
    """Get all active habits for current user."""
    user_id = get_current_user_id()
    habits = models.get_user_habits(user_id)
    return jsonify({"habits": habits})

@app.route("/api/habits", methods=["POST"])
def create_habit():
    """Create a new custom or predefined habit."""
    user_id = get_current_user_id()
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    category = data.get("category", "General").strip()
    color = data.get("color", "#8b5cf6")
    icon = data.get("icon", "✨")
    target = data.get("target", 7)
    goal = data.get("goal", "1x daily")

    if not name:
        return jsonify({"error": "Habit name is required"}), 400

    new_id = models.add_habit(user_id, name, category, color, icon, target, goal)
    return jsonify({"success": True, "habit_id": new_id})

@app.route("/api/habits/<int:habit_id>", methods=["PUT"])
def edit_habit(habit_id):
    """Edit an existing habit."""
    user_id = get_current_user_id()
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    category = data.get("category", "General").strip()
    color = data.get("color", "#8b5cf6")
    icon = data.get("icon", "✨")
    target = data.get("target", 7)
    goal = data.get("goal", "1x daily")

    if not name:
        return jsonify({"error": "Habit name is required"}), 400

    success = models.update_habit(user_id, habit_id, name, category, color, icon, target, goal)
    return jsonify({"success": success})

@app.route("/api/habits/<int:habit_id>", methods=["DELETE"])
def remove_habit(habit_id):
    """Delete a habit and its tracking history."""
    user_id = get_current_user_id()
    success = models.delete_habit(user_id, habit_id)
    return jsonify({"success": success})

# ==========================================
# TRACKER MATRIX & LOGGING APIS
# ==========================================

@app.route("/api/dashboard/monthly", methods=["GET"])
def monthly_dashboard():
    """
    Get full monthly habit tracker matrix:
    habits as rows, dates as columns, completion status, purple activity heatmap row.
    """
    user_id = get_current_user_id()
    today = datetime.date.today()

    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
    except ValueError:
        year = today.year
        month = today.month

    data = models.get_monthly_dashboard_data(user_id, year, month)
    return jsonify(data)

@app.route("/api/habits/toggle", methods=["POST"])
def toggle_habit():
    """
    Toggle completion status for a habit on a given date.
    Triggers streak calculations and motivational / savage quotes.
    """
    user_id = get_current_user_id()
    data = request.get_json() or {}
    habit_id = data.get("habit_id")
    date_str = data.get("date")
    custom_status = data.get("status")

    if not habit_id or not date_str:
        return jsonify({"error": "habit_id and date are required"}), 400

    result = models.toggle_habit_log(user_id, habit_id, date_str, custom_status)
    if not result:
        return jsonify({"error": "Habit not found"}), 404

    return jsonify(result)

# ==========================================
# ANALYTICS & DASHBOARD APIS
# ==========================================

@app.route("/api/statistics", methods=["GET"])
def statistics():
    """Get high-level statistics panels (Total completed, Streaks, Consistency)."""
    user_id = get_current_user_id()
    stats = models.calculate_overall_stats(user_id)
    return jsonify(stats)

@app.route("/api/analytics", methods=["GET"])
def analytics():
    """
    Get deep analytics:
    - Weekly progress & best day
    - Monthly progress & daily trends
    - Habit comparison & most consistent habit
    - Category distribution
    """
    user_id = get_current_user_id()
    data = models.get_analytics_data(user_id)
    return jsonify(data)

@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    """Get community leaderboard with current user ranking."""
    user_id = get_current_user_id()
    data = models.get_community_leaderboard(user_id)
    return jsonify({"leaderboard": data})

@app.route("/api/activity", methods=["GET"])
def activity():
    """Get recent activity feed items."""
    user_id = get_current_user_id()
    data = models.get_recent_activity(user_id)
    return jsonify({"activities": data})

# ==========================================
# PWA SUPPORT
# ==========================================

@app.route("/manifest.json")
def pwa_manifest():
    return app.send_static_file("manifest.json")

@app.route("/sw.js")
def pwa_service_worker():
    return app.send_static_file("sw.js")

if __name__ == "__main__":
    import webbrowser

    webbrowser.open("http://127.0.0.1:5000")

    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)