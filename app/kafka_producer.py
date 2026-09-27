import json
from kafka import KafkaProducer

# Kafka bağlantısını kurmaya çalışıyoruz
try:
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        # Verilerimizi Kafka'nın anlayacağı JSON formatına çeviriyoruz
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception:
    producer = None
    print("Not: Kafka sunucusu henüz aktif değil, Docker aşamasında devreye girecek.")

def send_cargo_event(event_type, cargo_id, tracking_number=None, status=None):
    if not producer:
        return # Kafka yoksa hata verme, sessizce geç
        
    # Gönderilecek mesajın iskeletini oluşturuyoruz[cite: 1]
    event_message = {"event": event_type}
    
    # İstenen formata göre mesajın içini dolduruyoruz[cite: 1]
    if event_type == "cargo.created":
        event_message["cargo_id"] = cargo_id
        event_message["tracking_number"] = tracking_number
    elif event_type == "cargo.status_changed":
        event_message["cargo_id"] = cargo_id
        event_message["status"] = status
    elif event_type == "cargo.delivered":
        event_message["cargo_id"] = cargo_id

    try:
        # Mesajı "cargo-events" isimli alana gönderiyoruz[cite: 1]
        producer.send('cargo-events', value=event_message)
        producer.flush() # Mesajın beklemeden anında gitmesini sağlar
    except Exception as e:
        print(f"Mesaj gönderilemedi: {e}")