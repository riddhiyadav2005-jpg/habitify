"""
models.py - Business logic, statistics, streak algorithms, and analytics calculations for Habitify.
"""

import calendar
import datetime
import random
from database import get_connection

# Motivational messages when habit is completed (Hype & Savage)
COMPLETION_QUOTES = [
    "THAT'S WHAT I'M TALKING ABOUT!",
    "Congratulations! You're moving closer to your next version.",
    "Look at you actually keeping promises to yourself.",
    "One step closer. Keep going!",
    "Look at this beast showing up today!",
    "Discipline > Motivation. You just proved it.",
    "Your future self is high-fiving you right now.",
    "Crushed it! You didn't fold.",
    "That's how champions build empires — one rep at a time.",
    "Another brick in the wall of discipline."
]

# Savage messages when a habit is genuinely missed (past days only!)
MISSED_QUOTES = [
    "HAHAHA, really thought you would go all in this time?",
    "Guess you don't want it bad enough.",
    "Your future self is watching.",
    "Okay, tomorrow we try again. No excuses.",
    "Rest day or excuse day? You decide.",
    "The mirror doesn't lie, and neither does this calendar.",
    "Discipline left the chat for a moment there, huh?",
    "Every day you skip, someone hungrier is doing the work."
]

# Milestone celebration messages for streaks
MILESTONE_QUOTES = {
    3: "🔥 3-Day Streak! The momentum has begun. Don't blink.",
    7: "⚡ 7-DAY UNSTOPPABLE STREAK! A whole week of absolute discipline!",
    14: "👑 14-Day Streak! You're operating on a different frequency now.",
    21: "🏆 21-Day Habit Milestone! Science says it's a habit now. No turning back.",
    30: "🚀 30 DAYS! LEGENDARY STATUS! You are officially in the top 1% of consistency."
}

def get_random_completion_quote():
    return random.choice(COMPLETION_QUOTES)

def get_random_missed_quote():
    return random.choice(MISSED_QUOTES)

# ==========================================
# HABIT CRUD OPERATIONS
# ==========================================

def get_user_habits(user_id):
    """Fetch all active habits for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM habits 
        WHERE user_id = ? AND is_active = 1 
        ORDER BY id ASC
    """, (user_id,))
    habits = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return habits

def add_habit(user_id, name, category, color="#8b5cf6", icon="✨", target=7, goal="1x daily"):
    """Create a new habit for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO habits (user_id, name, category, color, icon, target_days_per_week, daily_goal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name.strip(), category.strip(), color, icon, int(target), goal.strip()))
    new_id = cursor.lastrowid
    
    # Add activity entry
    cursor.execute("""
        INSERT INTO activity_feed (user_id, habit_name, action)
        VALUES (?, ?, ?)
    """, (user_id, name.strip(), f"Created new habit '{name.strip()}' ({category})"))
    
    conn.commit()
    conn.close()
    return new_id

def update_habit(user_id, habit_id, name, category, color, icon, target, goal):
    """Update an existing habit's properties."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE habits 
        SET name = ?, category = ?, color = ?, icon = ?, target_days_per_week = ?, daily_goal = ?
        WHERE id = ? AND user_id = ?
    """, (name.strip(), category.strip(), color, icon, int(target), goal.strip(), habit_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_habit(user_id, habit_id):
    """Soft delete or remove a habit and its logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
    habit = cursor.fetchone()
    habit_name = habit["name"] if habit else "Habit"

    cursor.execute("DELETE FROM habit_logs WHERE habit_id = ? AND user_id = ?", (habit_id, user_id))
    cursor.execute("DELETE FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
    
    cursor.execute("""
        INSERT INTO activity_feed (user_id, habit_name, action)
        VALUES (?, ?, ?)
    """, (user_id, habit_name, f"Deleted habit '{habit_name}'"))

    conn.commit()
    conn.close()
    return True

# ==========================================
# LOGGING AND TOGGLE COMPLETION
# ==========================================

def toggle_habit_log(user_id, habit_id, date_str, custom_status=None):
    """
    Toggle completion status for a habit on a specific date.
    Returns: dict with updated status, quote, streak info, milestone.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Validate habit belongs to user
    cursor.execute("SELECT name FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
    habit = cursor.fetchone()
    if not habit:
        conn.close()
        return None
    habit_name = habit["name"]

    # Check date vs today
    today = datetime.date.today()
    log_date = datetime.date.fromisoformat(date_str)
    is_future = log_date > today
    is_past = log_date < today
    is_today = log_date == today

    # Check existing log
    cursor.execute("""
        SELECT status FROM habit_logs 
        WHERE user_id = ? AND habit_id = ? AND date = ?
    """, (user_id, habit_id, date_str))
    existing = cursor.fetchone()

    new_status = ""
    quote = ""
    is_completed = False

    if custom_status:
        new_status = custom_status
    elif existing:
        if existing["status"] == "completed":
            # Unchecking: if it's a past date, it becomes 'missed', if today/future it gets removed
            if is_past:
                new_status = "missed"
            else:
                cursor.execute("DELETE FROM habit_logs WHERE user_id = ? AND habit_id = ? AND date = ?", 
                               (user_id, habit_id, date_str))
                new_status = "none"
        else: # Was missed or skipped -> toggle to completed
            new_status = "completed"
    else:
        # No log existed yet -> mark as completed
        new_status = "completed"

    if new_status in ["completed", "missed"]:
        cursor.execute("""
            INSERT INTO habit_logs (user_id, habit_id, date, status, notes)
            VALUES (?, ?, ?, ?, '')
            ON CONFLICT(habit_id, date) DO UPDATE SET status = excluded.status
        """, (user_id, habit_id, date_str, new_status))

    conn.commit()

    # Select appropriate motivational or savage quote
    milestone = None
    if new_status == "completed":
        is_completed = True
        quote = get_random_completion_quote()
        # Log to activity feed
        cursor.execute("""
            INSERT INTO activity_feed (user_id, habit_name, action)
            VALUES (?, ?, ?)
        """, (user_id, habit_name, f"Completed '{habit_name}' for {date_str} (+20 XP)"))
        conn.commit()
    elif new_status == "missed" or (existing and existing["status"] == "completed" and new_status == "none" and is_past):
        quote = get_random_missed_quote()

    # Calculate streaks for this habit
    habit_streak = calculate_habit_streak(user_id, habit_id, conn)
    overall_stats = calculate_overall_stats(user_id, conn)
    conn.close()

    if is_completed and habit_streak["current_streak"] in MILESTONE_QUOTES:
        milestone = MILESTONE_QUOTES[habit_streak["current_streak"]]

    return {
        "habit_id": habit_id,
        "date": date_str,
        "status": new_status,
        "quote": quote,
        "milestone": milestone,
        "habit_streak": habit_streak,
        "overall_stats": overall_stats
    }

# ==========================================
# STREAK CALCULATIONS
# ==========================================

def calculate_habit_streak(user_id, habit_id, conn=None):
    """
    Calculate current streak and longest streak for a single habit.
    Streaks require consecutive days marked 'completed'.
    """
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True

    cursor = conn.cursor()
    cursor.execute("""
        SELECT date FROM habit_logs 
        WHERE user_id = ? AND habit_id = ? AND status = 'completed'
        ORDER BY date ASC
    """, (user_id, habit_id))
    rows = cursor.fetchall()

    if close_at_end:
        conn.close()

    completed_dates = {datetime.date.fromisoformat(r["date"]) for r in rows}
    if not completed_dates:
        return {"current_streak": 0, "longest_streak": 0, "total_completed": 0}

    sorted_dates = sorted(list(completed_dates))
    total_completed = len(sorted_dates)

    # Calculate longest streak across history
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for d in sorted_dates:
        if prev_date is None:
            temp_streak = 1
        elif (d - prev_date).days == 1:
            temp_streak += 1
        else:
            temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak
        prev_date = d

    # Calculate current streak up to today (or yesterday if today isn't logged yet)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    current_streak = 0
    if today in completed_dates:
        current_streak = 1
        check_date = yesterday
        while check_date in completed_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
    elif yesterday in completed_dates:
        current_streak = 1
        check_date = yesterday - datetime.timedelta(days=1)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_completed": total_completed
    }

# ==========================================
# OVERALL STATISTICS
# ==========================================

def calculate_overall_stats(user_id, conn=None):
    """
    Calculate high-level dashboard metrics:
    - Total completed habits
    - Current streak (consecutive active days)
    - Longest streak
    - Overall completion percentage
    - Weekly consistency
    - Monthly consistency
    """
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True

    cursor = conn.cursor()

    # Total completed habits
    cursor.execute("""
        SELECT COUNT(*) FROM habit_logs 
        WHERE user_id = ? AND status = 'completed'
    """, (user_id,))
    total_completed = cursor.fetchone()[0]

    # Distinct dates where user completed at least 1 habit
    cursor.execute("""
        SELECT DISTINCT date FROM habit_logs 
        WHERE user_id = ? AND status = 'completed'
        ORDER BY date ASC
    """, (user_id,))
    date_rows = cursor.fetchall()
    active_dates = {datetime.date.fromisoformat(r["date"]) for r in date_rows}

    # Calculate overall longest streak & current streak
    sorted_active_dates = sorted(list(active_dates))
    longest_streak = 0
    temp_streak = 0
    prev_d = None
    for d in sorted_active_dates:
        if prev_d is None or (d - prev_d).days == 1:
            temp_streak += 1
        else:
            temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak
        prev_d = d

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    current_streak = 0
    if today in active_dates:
        current_streak = 1
        check_d = yesterday
        while check_d in active_dates:
            current_streak += 1
            check_d -= datetime.timedelta(days=1)
    elif yesterday in active_dates:
        current_streak = 1
        check_d = yesterday - datetime.timedelta(days=1)
        while check_d in active_dates:
            current_streak += 1
            check_d -= datetime.timedelta(days=1)

    # Active habits count
    cursor.execute("SELECT COUNT(*) FROM habits WHERE user_id = ? AND is_active = 1", (user_id,))
    active_habits_count = cursor.fetchone()[0]

    # Weekly consistency (past 7 days up to today)
    past_7_days = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    cursor.execute(f"""
        SELECT COUNT(*) FROM habit_logs 
        WHERE user_id = ? AND status = 'completed' AND date IN ({','.join(['?']*7)})
    """, [user_id] + past_7_days)
    week_completed = cursor.fetchone()[0]
    expected_week = max(1, active_habits_count * 7)
    weekly_consistency = min(100, round((week_completed / expected_week) * 100))

    # Monthly consistency (current month to date)
    first_of_month = today.replace(day=1)
    days_in_month_so_far = (today - first_of_month).days + 1
    cursor.execute("""
        SELECT COUNT(*) FROM habit_logs 
        WHERE user_id = ? AND status = 'completed' AND date >= ? AND date <= ?
    """, (user_id, first_of_month.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")))
    month_completed = cursor.fetchone()[0]
    expected_month = max(1, active_habits_count * days_in_month_so_far)
    monthly_consistency = min(100, round((month_completed / expected_month) * 100))

    # Overall completion percentage (all logs in database)
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
            COUNT(*) as total_logged
        FROM habit_logs 
        WHERE user_id = ?
    """, (user_id,))
    log_stats = cursor.fetchone()
    total_logged = log_stats["total_logged"] if log_stats else 0
    completed_count = log_stats["completed_count"] if log_stats else 0
    overall_percentage = round((completed_count / max(1, total_logged)) * 100) if total_logged > 0 else 0

    if close_at_end:
        conn.close()

    # Determine personality badge
    if current_streak >= 14:
        streak_badge = "🔥 Unstoppable Titan"
    elif current_streak >= 7:
        streak_badge = "⚡ On Fire"
    elif current_streak >= 3:
        streak_badge = "🚀 Gaining Momentum"
    elif current_streak >= 1:
        streak_badge = "🌱 Warming Up"
    else:
        streak_badge = "💤 Resting (Time to strike!)"

    return {
        "total_completed": total_completed,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "overall_percentage": overall_percentage,
        "weekly_consistency": weekly_consistency,
        "monthly_consistency": monthly_consistency,
        "streak_badge": streak_badge,
        "active_habits_count": active_habits_count
    }

# ==========================================
# MONTHLY DASHBOARD MATRIX
# ==========================================

def get_monthly_dashboard_data(user_id, year=None, month=None):
    """
    Generate matrix grid for habit tracker:
    - Days of the month (1..N) with day of week abbreviation (M, T, W...)
    - Habit rows with completion cells for each day
    - Distinguishes: completed, missed (past), not_yet_due (future)
    - Row completion totals and rates
    - Column completion sums (Heatmap row at the bottom)
    """
    today = datetime.date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Number of days in this month
    _, num_days = calendar.monthrange(year, month)
    month_name = calendar.month_name[month]

    days_info = []
    day_abbrs = ["M", "T", "W", "T", "F", "S", "S"]

    for d in range(1, num_days + 1):
        dt = datetime.date(year, month, d)
        days_info.append({
            "day_num": d,
            "weekday": day_abbrs[dt.weekday()],
            "date_str": dt.strftime("%Y-%m-%d"),
            "is_today": dt == today,
            "is_past": dt < today,
            "is_future": dt > today
        })

    # Fetch user habits
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM habits 
        WHERE user_id = ? AND is_active = 1 
        ORDER BY id ASC
    """, (user_id,))
    habits = [dict(r) for r in cursor.fetchall()]

    # Fetch logs for this month
    start_str = f"{year:04d}-{month:02d}-01"
    end_str = f"{year:04d}-{month:02d}-{num_days:02d}"

    cursor.execute("""
        SELECT habit_id, date, status 
        FROM habit_logs 
        WHERE user_id = ? AND date >= ? AND date <= ?
    """, (user_id, start_str, end_str))
    logs = cursor.fetchall()

    # Map logs: (habit_id, date) -> status
    log_map = {(r["habit_id"], r["date"]): r["status"] for r in logs}

    habit_rows = []
    daily_completion_counts = {d_info["date_str"]: 0 for d_info in days_info}

    for h in habits:
        h_id = h["id"]
        streak_info = calculate_habit_streak(user_id, h_id, conn)
        
        cells = []
        month_completions = 0
        evaluated_days = 0

        for d_info in days_info:
            d_str = d_info["date_str"]
            logged_status = log_map.get((h_id, d_str))

            if logged_status == "completed":
                cell_status = "completed"
                month_completions += 1
                daily_completion_counts[d_str] += 1
            elif d_info["is_future"]:
                cell_status = "not_yet_due"
            elif logged_status == "missed":
                cell_status = "missed"
            else:
                # Past day without explicit log is considered incomplete/missed
                cell_status = "incomplete"

            if not d_info["is_future"]:
                evaluated_days += 1

            cells.append({
                "date": d_str,
                "day_num": d_info["day_num"],
                "status": cell_status,
                "is_today": d_info["is_today"],
                "is_past": d_info["is_past"],
                "is_future": d_info["is_future"]
            })

        # Calculate rate for this month
        rate = round((month_completions / max(1, evaluated_days)) * 100) if evaluated_days > 0 else 0

        habit_rows.append({
            "id": h_id,
            "name": h["name"],
            "category": h["category"],
            "color": h["color"],
            "icon": h["icon"],
            "target": h["target_days_per_week"],
            "goal": h["daily_goal"],
            "streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "month_completions": month_completions,
            "month_rate": rate,
            "cells": cells
        })

    # Prepare bottom activity heatmap row
    heatmap_row = []
    max_possible = max(1, len(habits))
    for d_info in days_info:
        cnt = daily_completion_counts[d_info["date_str"]]
        intensity = 0
        if cnt > 0:
            ratio = cnt / max_possible
            if ratio <= 0.25:
                intensity = 1
            elif ratio <= 0.5:
                intensity = 2
            elif ratio <= 0.75:
                intensity = 3
            else:
                intensity = 4

        heatmap_row.append({
            "date": d_info["date_str"],
            "day_num": d_info["day_num"],
            "count": cnt,
            "intensity": intensity,
            "is_today": d_info["is_today"],
            "is_future": d_info["is_future"]
        })

    conn.close()

    return {
        "year": year,
        "month": month,
        "month_name": month_name,
        "days": days_info,
        "habits": habit_rows,
        "heatmap": heatmap_row,
        "total_habits": len(habits)
    }

# ==========================================
# ANALYTICS ENGINE (WEEKLY, MONTHLY, COMPARISON)
# ==========================================

def get_analytics_data(user_id):
    """
    Generate deep analytics calculated from actual habit logs:
    1. Weekly Analytics: Total per day (Mon-Sun), weekly completion %, best-performing day, Chart.js data
    2. Monthly Analytics: Total completed, monthly %, daily trends, Chart.js data
    3. Habit Comparison: Individual rates, most consistent habit, comparison Chart.js data
    4. Category Breakdown: Distribution across Fitness, Learning, Health, etc.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today()

    # 1. Weekly Analytics (current Monday to Sunday)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    week_dates = [start_of_week + datetime.timedelta(days=i) for i in range(7)]
    week_date_strs = [d.strftime("%Y-%m-%d") for d in week_dates]
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    cursor.execute(f"""
        SELECT date, COUNT(*) as count 
        FROM habit_logs 
        WHERE user_id = ? AND status = 'completed' AND date IN ({','.join(['?']*7)})
        GROUP BY date
    """, [user_id] + week_date_strs)
    week_logs = {r["date"]: r["count"] for r in cursor.fetchall()}

    weekly_counts = [week_logs.get(d_str, 0) for d_str in week_date_strs]
    total_weekly_completed = sum(weekly_counts)

    # Active habits count
    cursor.execute("SELECT COUNT(*) FROM habits WHERE user_id = ? AND is_active = 1", (user_id,))
    active_habits_count = max(1, cursor.fetchone()[0])

    # Days elapsed in current week so far
    days_elapsed_week = today.weekday() + 1
    expected_week_so_far = active_habits_count * days_elapsed_week
    weekly_completion_pct = min(100, round((total_weekly_completed / max(1, expected_week_so_far)) * 100))

    # Best-performing day
    best_day_idx = 0
    max_day_val = -1
    for i in range(days_elapsed_week):
        if weekly_counts[i] > max_day_val:
            max_day_val = weekly_counts[i]
            best_day_idx = i
    best_performing_day = f"{day_labels[best_day_idx]} ({max_day_val} habits completed)"

    # 2. Monthly Analytics (past 30 days)
    past_30_days = [today - datetime.timedelta(days=i) for i in range(29, -1, -1)]
    past_30_strs = [d.strftime("%Y-%m-%d") for d in past_30_days]
    past_30_labels = [d.strftime("%b %d") for d in past_30_days]

    cursor.execute(f"""
        SELECT date, COUNT(*) as count 
        FROM habit_logs 
        WHERE user_id = ? AND status = 'completed' AND date IN ({','.join(['?']*30)})
        GROUP BY date
    """, [user_id] + past_30_strs)
    month_trend_logs = {r["date"]: r["count"] for r in cursor.fetchall()}

    monthly_counts = [month_trend_logs.get(d_str, 0) for d_str in past_30_strs]
    total_monthly_completed = sum(monthly_counts)
    monthly_expected = active_habits_count * 30
    monthly_completion_pct = min(100, round((total_monthly_completed / max(1, monthly_expected)) * 100))

    # 3. Habit Comparison (Consistency across last 30 days)
    cursor.execute("""
        SELECT h.id, h.name, h.category, h.color, h.icon,
               COUNT(hl.id) as completions
        FROM habits h
        LEFT JOIN habit_logs hl 
            ON h.id = hl.habit_id 
            AND hl.status = 'completed' 
            AND hl.date >= ? AND hl.date <= ?
        WHERE h.user_id = ? AND h.is_active = 1
        GROUP BY h.id
        ORDER BY completions DESC
    """, (past_30_strs[0], past_30_strs[-1], user_id))
    habit_rows = cursor.fetchall()

    habit_comparison = []
    most_consistent_habit = "None yet"
    highest_rate = -1

    for row in habit_rows:
        comp = row["completions"]
        rate = round((comp / 30.0) * 100)
        habit_comparison.append({
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "color": row["color"],
            "icon": row["icon"],
            "completions": comp,
            "percentage": min(100, rate)
        })
        if rate > highest_rate:
            highest_rate = rate
            most_consistent_habit = f"{row['icon']} {row['name']} ({min(100, rate)}%)"

    # 4. Category breakdown
    cursor.execute("""
        SELECT h.category, COUNT(hl.id) as completions
        FROM habits h
        JOIN habit_logs hl ON h.id = hl.habit_id AND hl.status = 'completed'
        WHERE h.user_id = ?
        GROUP BY h.category
        ORDER BY completions DESC
    """, (user_id,))
    cat_rows = cursor.fetchall()
    category_labels = [r["category"] for r in cat_rows]
    category_values = [r["completions"] for r in cat_rows]

    conn.close()

    return {
        "weekly": {
            "labels": day_labels,
            "data": weekly_counts,
            "total_completed": total_weekly_completed,
            "percentage": weekly_completion_pct,
            "best_day": best_performing_day
        },
        "monthly": {
            "labels": past_30_labels,
            "data": monthly_counts,
            "total_completed": total_monthly_completed,
            "percentage": monthly_completion_pct
        },
        "comparison": {
            "habits": habit_comparison,
            "most_consistent": most_consistent_habit,
            "labels": [h["name"] for h in habit_comparison],
            "percentages": [h["percentage"] for h in habit_comparison],
            "colors": [h["color"] for h in habit_comparison]
        },
        "categories": {
            "labels": category_labels if category_labels else ["General"],
            "values": category_values if category_values else [1]
        }
    }

# ==========================================
# COMMUNITY LEADERBOARD & RECENT ACTIVITY
# ==========================================

def get_community_leaderboard(current_user_id):
    """
    Fetch global/community habit tracking leaderboard.
    Ranks users by streak points and consistency score.
    """
    # Sample community champions + current user
    community_members = [
        {"rank": 1, "username": "sarah_zen", "name": "Sarah Jenkins", "avatar": "🧘‍♀️", "streak": 42, "xp": 1420, "score": 98, "status": "Grandmaster"},
        {"rank": 2, "username": "marcus_lift", "name": "Marcus Vance", "avatar": "⚡", "streak": 28, "xp": 980, "score": 94, "status": "Beast Mode"},
        {"rank": 3, "username": "elena_code", "name": "Elena Rostova", "avatar": "🚀", "streak": 21, "xp": 790, "score": 91, "status": "Disciplined"},
        {"rank": 4, "username": "kenji_run", "name": "Kenji Sato", "avatar": "🏃‍♂️", "streak": 19, "xp": 680, "score": 88, "status": "Consistent"}
    ]

    stats = calculate_overall_stats(current_user_id)
    user_xp = (stats["total_completed"] * 20) + (stats["current_streak"] * 50)

    # Determine user rank among champions
    user_entry = {
        "rank": 5,
        "username": "you",
        "name": "You",
        "avatar": "🔥",
        "streak": stats["current_streak"],
        "xp": user_xp,
        "score": stats["weekly_consistency"],
        "status": stats["streak_badge"],
        "is_current_user": True
    }

    # Insert user into appropriate leaderboard position
    all_ranks = community_members + [user_entry]
    all_ranks.sort(key=lambda x: (x["streak"], x["score"]), reverse=True)

    for idx, member in enumerate(all_ranks):
        member["rank"] = idx + 1

    return all_ranks

def get_recent_activity(user_id, limit=8):
    """Fetch recent activity feed entries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT habit_name, action, timestamp 
        FROM activity_feed 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]
