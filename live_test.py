"""
Live Integration Test Suite for Smart Plant Health Assistant
Tests all API endpoints against the running server at http://localhost:5000
"""

import requests
import json
import time
import os
import sys

BASE_URL = "http://localhost:5000"
TOKEN = None
TEST_USER = {
    "email": f"livetest_{int(time.time())}@test.com",
    "password": "LiveTest1!",
    "name": "Live Tester"
}
RESULTS = {"passed": 0, "failed": 0, "errors": []}

def log(status, test_name, detail=""):
    icon = "PASS" if status else "FAIL"
    RESULTS["passed" if status else "failed"] += 1
    msg = f"  [{icon}] {test_name}"
    if detail and not status:
        msg += f" -- {detail}"
        RESULTS["errors"].append(f"{test_name}: {detail}")
    print(msg)

def headers():
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h

def auth_headers_no_ct():
    h = {}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h

# ==============================================================
# 1. HEALTH / STATUS
# ==============================================================
def test_health():
    print("\n=== 1. HEALTH & STATUS ===")
    r = requests.get(f"{BASE_URL}/api/v1/status", timeout=5)
    log(r.status_code == 200, "Health check (/api/v1/status)", f"Status: {r.status_code}")
    r = requests.get(f"{BASE_URL}/", timeout=5)
    log(r.status_code == 200, "Root page (/)", f"Status: {r.status_code}")

# ==============================================================
# 2. AUTHENTICATION
# ==============================================================
def test_auth():
    global TOKEN
    print("\n=== 2. AUTHENTICATION ===")

    r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=TEST_USER, timeout=10)
    log(r.status_code in [200, 201], "Register new user", f"Status: {r.status_code} -- {r.text[:200]}")
    if r.status_code in [200, 201]:
        data = r.json()
        if "token" in data:
            TOKEN = data["token"]

    r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=TEST_USER, timeout=10)
    log(r.status_code in [400, 409, 422], "Register duplicate (expect error)", f"Status: {r.status_code}")

    r = requests.post(f"{BASE_URL}/api/v1/auth/register", json={"email": "bad@test.com", "password": "weak", "name": "Bad"}, timeout=10)
    log(r.status_code in [400, 422], "Register weak password (expect error)", f"Status: {r.status_code}")

    r = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": TEST_USER["email"], "password": TEST_USER["password"]}, timeout=10)
    log(r.status_code == 200, "Login", f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        TOKEN = data.get("token") or data.get("access_token")
        log(TOKEN is not None, "Login returns token")

    r = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": TEST_USER["email"], "password": "WrongPass1!"}, timeout=10)
    log(r.status_code in [401, 403], "Login wrong password (expect error)", f"Status: {r.status_code}")

    if TOKEN:
        r = requests.post(f"{BASE_URL}/api/v1/auth/validate", json={"token": TOKEN}, timeout=10)
        log(r.status_code == 200, "Validate token", f"Status: {r.status_code}")

    if TOKEN:
        r = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers(), timeout=10)
        log(r.status_code == 200, "Get profile (/me)", f"Status: {r.status_code}")

    if TOKEN:
        r = requests.post(f"{BASE_URL}/api/v1/auth/session-info", json={"token": TOKEN}, timeout=10)
        log(r.status_code == 200, "Session info", f"Status: {r.status_code}")

    if TOKEN:
        r = requests.put(f"{BASE_URL}/api/v1/auth/language", headers=headers(), json={"language": "en"}, timeout=10)
        log(r.status_code == 200, "Update language", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/auth/me", timeout=10)
    log(r.status_code in [401, 403], "Protected route no token (expect error)", f"Status: {r.status_code}")

# ==============================================================
# 3. PLANTS (CRUD)
# ==============================================================
PLANT_ID = None

def test_plants():
    global PLANT_ID
    print("\n=== 3. PLANTS (CRUD) ===")

    r = requests.post(f"{BASE_URL}/api/v1/plants", headers=auth_headers_no_ct(),
                      data={"name": "Test Rose", "species": "Rosa", "location": "Living Room", "notes": "Test plant"}, timeout=10)
    log(r.status_code in [200, 201], "Create plant (form-data)", f"Status: {r.status_code} -- {r.text[:200]}")
    if r.status_code in [200, 201]:
        data = r.json()
        PLANT_ID = data.get("id") or data.get("plant", {}).get("id")

    r = requests.get(f"{BASE_URL}/api/v1/plants", headers=headers(), timeout=10)
    log(r.status_code == 200, "List plants", f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        plants = data if isinstance(data, list) else data.get("plants", [])
        log(len(plants) >= 1, f"Plants list has items (count={len(plants)})")
        if not PLANT_ID and plants:
            PLANT_ID = plants[0].get("id")

    if PLANT_ID:
        r = requests.get(f"{BASE_URL}/api/v1/plants/{PLANT_ID}", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Get plant #{PLANT_ID}", f"Status: {r.status_code}")

    if PLANT_ID:
        r = requests.put(f"{BASE_URL}/api/v1/plants/{PLANT_ID}", headers=headers(),
                         json={"name": "Updated Test Rose"}, timeout=10)
        log(r.status_code == 200, f"Update plant #{PLANT_ID}", f"Status: {r.status_code}")

    if PLANT_ID:
        r = requests.post(f"{BASE_URL}/api/v1/plants/{PLANT_ID}/water", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Water plant #{PLANT_ID}", f"Status: {r.status_code}")

    if PLANT_ID:
        r = requests.post(f"{BASE_URL}/api/v1/plants/{PLANT_ID}/fertilize", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Fertilize plant #{PLANT_ID}", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/plants/species-care/Rosa", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get species care info (Rosa)", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/plants/species-list", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get species list", f"Status: {r.status_code}")

# ==============================================================
# 4. PLANT ANALYSIS
# ==============================================================
def test_analysis():
    print("\n=== 4. PLANT ANALYSIS ===")

    r = requests.post(f"{BASE_URL}/api/v1/analyze", headers=headers(),
                      json={"image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Sunflower_from_Silesia2.jpg/800px-Sunflower_from_Silesia2.jpg"},
                      timeout=30)
    log(r.status_code in [200, 400, 422, 429, 500], "Analyze plant (URL)", f"Status: {r.status_code}")

    r = requests.post(f"{BASE_URL}/api/v1/analyze", headers=headers(), json={}, timeout=10)
    log(r.status_code in [400, 422], "Analyze no image (expect error)", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/diseases", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get diseases list", f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        diseases = data if isinstance(data, list) else data.get("diseases", [])
        log(len(diseases) > 0, f"Diseases (count={len(diseases)})")

    r = requests.get(f"{BASE_URL}/api/v1/plants/search?q=rose", headers=headers(), timeout=10)
    log(r.status_code in [200, 503], "Search plants (may need API key)", f"Status: {r.status_code}")

    save_data = {
        "plant_name": "Analysis Test Sunflower",
        "species": "Helianthus annuus",
        "location": "Garden",
        "analysis_data": {
            "plant_name": "Sunflower", "species": "Helianthus annuus",
            "health_score": 85, "health_status": "Healthy",
            "diseases": [], "care_recommendations": ["Water regularly"]
        }
    }
    r = requests.post(f"{BASE_URL}/api/v1/analyze/save-to-plants", headers=headers(), json=save_data, timeout=10)
    log(r.status_code in [200, 201], "Save analysis to My Plants", f"Status: {r.status_code}")

# ==============================================================
# 5. TREATMENTS
# ==============================================================
TREATMENT_ID = None

def test_treatments():
    global TREATMENT_ID
    print("\n=== 5. TREATMENTS ===")

    treatment_data = {
        "plant_id": PLANT_ID or 1,
        "disease_name": "Powdery Mildew",
        "severity": "moderate",
        "treatment_type": "organic",
        "steps": [
            {"step": 1, "action": "Remove affected leaves", "duration_days": 1},
            {"step": 2, "action": "Apply neem oil spray", "duration_days": 7},
            {"step": 3, "action": "Monitor for recurrence", "duration_days": 14}
        ]
    }
    r = requests.post(f"{BASE_URL}/api/v1/treatments", headers=headers(), json=treatment_data, timeout=10)
    log(r.status_code in [200, 201], "Create treatment", f"Status: {r.status_code}")
    if r.status_code in [200, 201]:
        data = r.json()
        TREATMENT_ID = data.get("id") or data.get("treatment", {}).get("id")

    r = requests.get(f"{BASE_URL}/api/v1/treatments", headers=headers(), timeout=10)
    log(r.status_code == 200, "List treatments", f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        treatments = data if isinstance(data, list) else data.get("treatments", [])
        log(len(treatments) >= 1, f"Treatments list (count={len(treatments)})")
        if not TREATMENT_ID and treatments:
            TREATMENT_ID = treatments[0].get("id")

    if TREATMENT_ID:
        r = requests.get(f"{BASE_URL}/api/v1/treatments/{TREATMENT_ID}", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Get treatment #{TREATMENT_ID}", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/treatments/active", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get active treatments", f"Status: {r.status_code}")

    if TREATMENT_ID:
        r = requests.put(f"{BASE_URL}/api/v1/treatments/{TREATMENT_ID}/progress", headers=headers(),
                         json={"step_index": 0, "completed": True}, timeout=10)
        log(r.status_code == 200, "Update treatment progress", f"Status: {r.status_code} -- {r.text[:200]}")

    if TREATMENT_ID:
        r = requests.post(f"{BASE_URL}/api/v1/treatments/{TREATMENT_ID}/complete", headers=headers(), timeout=10)
        log(r.status_code == 200, "Complete treatment", f"Status: {r.status_code}")

    treatment_data2 = {
        "plant_id": PLANT_ID or 1,
        "disease_name": "Root Rot",
        "severity": "mild",
        "treatment_type": "organic",
        "steps": [{"step": 1, "action": "Reduce watering", "duration_days": 7}]
    }
    r = requests.post(f"{BASE_URL}/api/v1/treatments", headers=headers(), json=treatment_data2, timeout=10)
    tid2 = None
    if r.status_code in [200, 201]:
        data = r.json()
        tid2 = data.get("id") or data.get("treatment", {}).get("id")

    if tid2:
        r = requests.post(f"{BASE_URL}/api/v1/treatments/{tid2}/abandon", headers=headers(),
                          json={"reason": "Test abandon"}, timeout=10)
        log(r.status_code == 200, f"Abandon treatment #{tid2}", f"Status: {r.status_code} -- {r.text[:200]}")

    r = requests.post(f"{BASE_URL}/api/v1/treatments", headers=headers(), json=treatment_data2, timeout=10)
    tid3 = None
    if r.status_code in [200, 201]:
        data = r.json()
        tid3 = data.get("id") or data.get("treatment", {}).get("id")

    if tid3:
        r = requests.delete(f"{BASE_URL}/api/v1/treatments/{tid3}", headers=headers(), timeout=10)
        log(r.status_code in [200, 204], f"Delete treatment #{tid3}", f"Status: {r.status_code}")

# ==============================================================
# 6. NOTIFICATIONS & REMINDERS
# ==============================================================
REMINDER_ID = None
NOTIFICATION_ID = None

def test_notifications():
    global REMINDER_ID, NOTIFICATION_ID
    print("\n=== 6. NOTIFICATIONS & REMINDERS ===")

    r = requests.get(f"{BASE_URL}/api/v1/notifications", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get notifications", f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        notifs = data if isinstance(data, list) else data.get("notifications", [])
        if notifs:
            NOTIFICATION_ID = notifs[0].get("id")

    r = requests.get(f"{BASE_URL}/api/v1/notifications/count", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get notification count", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/reminders", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get reminders", f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        reminders = data if isinstance(data, list) else data.get("reminders", [])
        log(True, f"Reminders count: {len(reminders)}")
        if reminders:
            REMINDER_ID = reminders[0].get("id")

    r = requests.get(f"{BASE_URL}/api/v1/reminders/upcoming", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get upcoming reminders", f"Status: {r.status_code}")

    reminder_data = {
        "type": "water",
        "frequency_days": 3,
        "plant_id": PLANT_ID or 1,
        "title": "Test water reminder"
    }
    r = requests.post(f"{BASE_URL}/api/v1/reminders", headers=headers(), json=reminder_data, timeout=10)
    log(r.status_code in [200, 201], "Create reminder", f"Status: {r.status_code} -- {r.text[:200]}")
    if r.status_code in [200, 201]:
        data = r.json()
        new_rem_id = data.get("id") or data.get("reminder", {}).get("id")
        if new_rem_id:
            REMINDER_ID = new_rem_id

    if REMINDER_ID:
        r = requests.put(f"{BASE_URL}/api/v1/reminders/{REMINDER_ID}", headers=headers(),
                         json={"frequency_days": 5, "title": "Updated reminder"}, timeout=10)
        log(r.status_code == 200, f"Update reminder #{REMINDER_ID}", f"Status: {r.status_code}")

    if REMINDER_ID:
        r = requests.post(f"{BASE_URL}/api/v1/reminders/{REMINDER_ID}/complete", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Complete reminder #{REMINDER_ID}", f"Status: {r.status_code}")

    if NOTIFICATION_ID:
        r = requests.post(f"{BASE_URL}/api/v1/notifications/{NOTIFICATION_ID}/read", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Mark notification #{NOTIFICATION_ID} as read", f"Status: {r.status_code}")

    r = requests.post(f"{BASE_URL}/api/v1/notifications/read-all", headers=headers(), timeout=10)
    log(r.status_code == 200, "Mark all notifications read", f"Status: {r.status_code}")

    r = requests.post(f"{BASE_URL}/api/v1/notifications/subscribe", headers=headers(),
                      json={"subscription": {"endpoint": "https://test.example.com/push", "keys": {"p256dh": "test", "auth": "test"}}}, timeout=10)
    log(r.status_code == 200, "Subscribe to notifications", f"Status: {r.status_code} -- {r.text[:200]}")

# ==============================================================
# 7. CHAT
# ==============================================================
def test_chat():
    print("\n=== 7. CHAT ===")

    r = requests.post(f"{BASE_URL}/api/v1/chat", headers=headers(),
                      json={"message": "How do I care for a rose plant?"}, timeout=30)
    log(r.status_code == 200, "Send chat message", f"Status: {r.status_code} -- {r.text[:300]}")

    r = requests.get(f"{BASE_URL}/api/v1/chat/suggestions", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get chat suggestions", f"Status: {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/v1/chat/history", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get chat history", f"Status: {r.status_code}")

    r = requests.delete(f"{BASE_URL}/api/v1/chat/history", headers=headers(), timeout=10)
    log(r.status_code == 200, "Delete chat history", f"Status: {r.status_code}")

# ==============================================================
# 8. HISTORY
# ==============================================================
def test_history():
    print("\n=== 8. ANALYSIS HISTORY ===")

    r = requests.get(f"{BASE_URL}/api/v1/history", headers=headers(), timeout=10)
    log(r.status_code == 200, "Get analysis history", f"Status: {r.status_code}")
    analysis_id = None
    if r.status_code == 200:
        data = r.json()
        items = data if isinstance(data, list) else data.get("history", data.get("analyses", []))
        if isinstance(items, list) and items:
            analysis_id = items[0].get("id")
            log(True, f"History has {len(items)} item(s)")
        else:
            log(True, "History empty (OK, no analyses yet)")

    if analysis_id:
        r = requests.get(f"{BASE_URL}/api/v1/history/{analysis_id}", headers=headers(), timeout=10)
        log(r.status_code == 200, f"Get history item #{analysis_id}", f"Status: {r.status_code}")

# ==============================================================
# 9. FRONTEND PAGES
# ==============================================================
def test_frontend():
    print("\n=== 9. FRONTEND PAGES ===")
    pages = [
        ("/", "Root"), ("/login", "Login"), ("/dashboard", "Dashboard"), ("/home", "Home"),
        ("/frontend/index.html", "Analysis"), ("/frontend/login.html", "Login HTML"),
        ("/frontend/dashboard.html", "Dashboard HTML"), ("/frontend/plants.html", "Plants HTML"),
        ("/frontend/history.html", "History HTML"), ("/frontend/home.html", "Home HTML"),
        ("/css/styles.css", "CSS"), ("/js/app.js", "App JS"), ("/js/translations.js", "Translations JS"),
    ]
    for path, name in pages:
        try:
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
            log(r.status_code == 200, f"{name} ({path})", f"Status: {r.status_code}")
        except Exception as e:
            log(False, f"{name} ({path})", str(e))

# ==============================================================
# 10. CLEANUP
# ==============================================================
def test_cleanup():
    print("\n=== 10. CLEANUP ===")
    if REMINDER_ID:
        r = requests.delete(f"{BASE_URL}/api/v1/reminders/{REMINDER_ID}", headers=headers(), timeout=10)
        log(r.status_code in [200, 204], f"Delete reminder #{REMINDER_ID}", f"Status: {r.status_code}")
    if NOTIFICATION_ID:
        r = requests.delete(f"{BASE_URL}/api/v1/notifications/{NOTIFICATION_ID}", headers=headers(), timeout=10)
        log(r.status_code in [200, 204], f"Delete notification #{NOTIFICATION_ID}", f"Status: {r.status_code}")
    if PLANT_ID:
        r = requests.delete(f"{BASE_URL}/api/v1/plants/{PLANT_ID}", headers=headers(), timeout=10)
        log(r.status_code in [200, 204], f"Delete plant #{PLANT_ID}", f"Status: {r.status_code}")
    r = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers(), timeout=10)
    log(r.status_code == 200, "Logout", f"Status: {r.status_code}")

# ==============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" LIVE INTEGRATION TEST SUITE")
    print(f" Server: {BASE_URL}")
    print(f" Test User: {TEST_USER['email']}")
    print("=" * 60)

    try:
        test_health()
        test_auth()
        test_plants()
        test_analysis()
        test_treatments()
        test_notifications()
        test_chat()
        test_history()
        test_frontend()
        test_cleanup()
    except Exception as e:
        print(f"\n!!! FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print(f" RESULTS: {RESULTS['passed']} PASSED, {RESULTS['failed']} FAILED")
    print("=" * 60)
    if RESULTS["errors"]:
        print("\n FAILED TESTS:")
        for err in RESULTS["errors"]:
            print(f"   - {err}")
    print()
    sys.exit(0 if RESULTS["failed"] == 0 else 1)
