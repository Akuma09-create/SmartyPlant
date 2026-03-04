import requests
BASE='http://localhost:5000'
r=requests.post(f'{BASE}/api/v1/auth/login',json={'email':'livetest_1771519222@test.com','password':'LiveTest1!'})
tok=r.json().get('token')
h={'Authorization':f'Bearer {tok}','Content-Type':'application/json'}

pages=['/frontend/login.html','/frontend/dashboard.html','/frontend/plants.html','/frontend/history.html','/frontend/home.html','/css/styles.css','/js/app.js','/js/translations.js']
for p in pages:
    r2=requests.get(f'{BASE}{p}',timeout=5)
    status = "PASS" if r2.status_code==200 else "FAIL"
    print(f"  [{status}] {p} -> {r2.status_code}")

# Also run the cleanup/logout test
r3=requests.post(f'{BASE}/api/v1/auth/logout',headers=h,timeout=10)
print(f"  [{'PASS' if r3.status_code==200 else 'FAIL'}] Logout -> {r3.status_code}")
