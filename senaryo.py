import requests
import time

BASE_URL = "http://localhost:5000"

print("Senaryo başlatılıyor...")

# 1. 20 adet kargo oluştur
cargo_ids = []
for i in range(1, 21):
    resp = requests.post(f"{BASE_URL}/cargo", json={
        "tracking_number": f"KRG-200{i}",
        "sender": "Sıla",
        "receiver": "Orhan"
    })
    cargo_ids.append(resp.json()['id'])

print("20 kargo oluşturuldu.")
time.sleep(1)

# 2. 10 kargonun durumunu IN_TRANSIT yap[cite: 1]
for i in range(10):
    requests.put(f"{BASE_URL}/cargo/{cargo_ids[i]}/status", json={"status": "IN_TRANSIT"})
print("10 kargo IN_TRANSIT yapıldı.")
time.sleep(1)

# 3. 5 kargoyu DELIVERED durumuna getir[cite: 1]
for i in range(5):
    requests.put(f"{BASE_URL}/cargo/{cargo_ids[i]}/status", json={"status": "DELIVERED"})
print("5 kargo DELIVERED yapıldı.")
time.sleep(1)

# 4. 2 kargoyu iptal et[cite: 1]
for i in range(10, 12):
    requests.put(f"{BASE_URL}/cargo/{cargo_ids[i]}/status", json={"status": "CANCELLED"})
print("2 kargo CANCELLED yapıldı.")

print("Senaryo tamamlandı! Veriler Grafana'ya aktarıldı.")