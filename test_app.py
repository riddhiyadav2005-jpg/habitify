"""
test_app.py - Automated test suite for Habitify endpoints and core business logic
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import json
from app import app

def run_tests():
    client = app.test_client()

    print("Running Habitify Automated Test Suite...")

    # 1. Test index page
    res = client.get('/')
    assert res.status_code == 200, f"Index failed: {res.status_code}"
    assert b"Habitify" in res.data, "Habitify text not found in index"
    print("  [PASS] 1. Index page served successfully")

    # 2. Test Auth Me
    res = client.get('/api/auth/me')
    assert res.status_code == 200
    data = res.get_json()
    assert data['authenticated'] is True
    assert data['user']['username'] == 'demo_user'
    print(f"  [PASS] 2. User authentication endpoint: loaded {data['user']['display_name']}")

    # 3. Test Monthly Dashboard
    res = client.get('/api/dashboard/monthly?year=2026&month=11')
    assert res.status_code == 200
    m_data = res.get_json()
    assert 'habits' in m_data
    assert len(m_data['habits']) >= 7, f"Expected at least 7 default habits, got {len(m_data['habits'])}"
    assert 'heatmap' in m_data
    print(f"  [PASS] 3. Monthly tracker matrix: {len(m_data['habits'])} habits and {len(m_data['heatmap'])} day heatmap loaded")

    # 4. Test Statistics
    res = client.get('/api/statistics')
    assert res.status_code == 200
    stats = res.get_json()
    print(f"  [PASS] 4. Statistics: Total={stats['total_completed']}, Streak={stats['current_streak']}d, Record={stats['longest_streak']}d, Consistency={stats['monthly_consistency']}%")

    # 5. Test Analytics
    res = client.get('/api/analytics')
    assert res.status_code == 200
    analytics = res.get_json()
    assert 'weekly' in analytics and 'monthly' in analytics and 'comparison' in analytics
    print(f"  [PASS] 5. Analytics: Weekly={analytics['weekly']['percentage']}%, Most consistent={analytics['comparison']['most_consistent']}")

    # 6. Test Habit Toggle
    h_id = m_data['habits'][0]['id']
    res = client.post('/api/habits/toggle', json={'habit_id': h_id, 'date': '2026-11-02'})
    assert res.status_code == 200
    toggle_res = res.get_json()
    print(f"  [PASS] 6. Habit toggle: status={toggle_res['status']}, quote='{toggle_res['quote']}'")

    # 7. Test Add Custom Habit
    res = client.post('/api/habits', json={
        'name': 'Cold Shower',
        'category': 'Health',
        'color': '#06b6d4',
        'icon': '🚿',
        'target': 7,
        'goal': '3 mins ice cold'
    })
    assert res.status_code == 200
    new_h_id = res.get_json()['habit_id']
    print(f"  [PASS] 7. Custom habit created: ID={new_h_id}")

    # 8. Test Edit Habit
    res = client.put(f'/api/habits/{new_h_id}', json={
        'name': 'Cold Shower & Ice Bath',
        'category': 'Health',
        'color': '#06b6d4',
        'icon': '❄️',
        'target': 7,
        'goal': '5 mins ice cold'
    })
    assert res.status_code == 200
    print("  [PASS] 8. Habit updated successfully")

    # 9. Test Delete Habit
    res = client.delete(f'/api/habits/{new_h_id}')
    assert res.status_code == 200
    print("  [PASS] 9. Habit deleted successfully")

    # 10. Test Leaderboard and Activity
    res = client.get('/api/leaderboard')
    assert res.status_code == 200
    leaders = res.get_json()['leaderboard']
    print(f"  [PASS] 10a. Leaderboard: {len(leaders)} users ranked")

    res = client.get('/api/activity')
    assert res.status_code == 200
    activities = res.get_json()['activities']
    print(f"  [PASS] 10b. Activity stream: {len(activities)} items logged")

    print("\n==============================================")
    print(" ALL 10 TESTS PASSED SUCCESSFULLY! ")
    print("==============================================")

if __name__ == '__main__':
    run_tests()
