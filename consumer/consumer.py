import json
import time
from kafka import KafkaConsumer

print("Kafka Consumer başlatılıyor... (Kafka sunucusu bekleniyor)")

# Gerçek Kafka sunucusu Docker ile ayağa kalkana kadar hata vermemesi için
# bağlanmayı sürekli deneyen bir döngü kuruyoruz.
while True:
    try:
        consumer = KafkaConsumer(
            'cargo-events', # Dinleyeceğimiz alanın (topic) adı
            bootstrap_servers=['kafka:9092', 'localhost:9092'], # Hem Docker hem yerel bağlantı için
            auto_offset_reset='earliest', # Kaçırdığımız eski mesajları da baştan oku
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        print("Kafka'ya başarıyla bağlandı! Kargo olayları dinleniyor...\n")
        break
    except Exception:
        print("Kafka sunucusu henüz aktif değil, 5 saniye sonra tekrar denenecek...")
        time.sleep(5)

# Zil çaldığında (mesaj geldiğinde) yapılacak işlemler[cite: 1]
for message in consumer:
    event_data = message.value
    event_type = event_data.get("event")
    cargo_id = event_data.get("cargo_id")

    # İstenen formata göre terminale mesaj yazdırıyoruz[cite: 1]
    if event_type == "cargo.delivered":
        print(f"Cargo {cargo_id} delivered.")
    elif event_type == "cargo.status_changed":
        status = event_data.get("status")
        print(f"Cargo {cargo_id} status changed to {status}.")
    elif event_type == "cargo.created":
        tracking_number = event_data.get("tracking_number")
        print(f"Cargo {cargo_id} created with tracking number {tracking_number}.")