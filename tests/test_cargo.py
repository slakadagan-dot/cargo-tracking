import pytest
from app import create_app

# Testler için sanal bir sunucu (client) oluşturuyoruz
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test 1: Geçerli bilgilerle kargo oluşturulabiliyor mu?[cite: 1]
def test_1_create_valid_cargo(client):
    response = client.post('/cargo', json={
        "tracking_number": "KRG-1001",
        "sender": "Ahmet",
        "receiver": "Mehmet"
    })
    assert response.status_code == 201

# Test 2: Tracking number boş bırakıldığında sistem hata veriyor mu?[cite: 1]
def test_2_create_cargo_without_tracking_number(client):
    response = client.post('/cargo', json={
        "sender": "Ahmet",
        "receiver": "Mehmet"
    })
    assert response.status_code == 400

# Test 3: Olmayan kargo sorgulandığında HTTP 404 dönüyor mu?[cite: 1]
def test_3_get_nonexistent_cargo(client):
    response = client.get('/cargo/99999')
    assert response.status_code == 404

# Test 4: Kargo durumu değiştirilebiliyor mu?[cite: 1]
def test_4_update_cargo_status(client):
    # Önce kargo oluşturuyoruz
    create_resp = client.post('/cargo', json={"tracking_number": "KRG-TEST4", "sender": "A", "receiver": "B"})
    cargo_id = create_resp.get_json()['id']
    
    # Sonra durumunu IN_TRANSIT yapıyoruz
    response = client.put(f'/cargo/{cargo_id}/status', json={"status": "IN_TRANSIT"})
    assert response.status_code == 200
    assert response.get_json()['status'] == "IN_TRANSIT"

# Test 5: Geçersiz durum gönderildiğinde hata dönüyor mu?[cite: 1]
def test_5_invalid_status_update(client):
    create_resp = client.post('/cargo', json={"tracking_number": "KRG-TEST5", "sender": "A", "receiver": "B"})
    cargo_id = create_resp.get_json()['id']
    
    response = client.put(f'/cargo/{cargo_id}/status', json={"status": "HATALI_DURUM"})
    assert response.status_code == 400

# Test 6: Teslim edilmiş kargo tekrar dağıtıma çıkarılamasın[cite: 1]
def test_6_update_delivered_cargo(client):
    create_resp = client.post('/cargo', json={"tracking_number": "KRG-TEST6", "sender": "A", "receiver": "B"})
    cargo_id = create_resp.get_json()['id']
    
    # Önce teslim edildi yapıyoruz
    client.put(f'/cargo/{cargo_id}/status', json={"status": "DELIVERED"})
    
    # Sonra tekrar dağıtıma çıkarmaya çalışıyoruz (Hata 400 dönmeli)
    response = client.put(f'/cargo/{cargo_id}/status', json={"status": "IN_TRANSIT"})
    assert response.status_code == 400

# Test 7: Kargo silinebiliyor mu?[cite: 1]
def test_7_delete_cargo(client):
    create_resp = client.post('/cargo', json={"tracking_number": "KRG-TEST7", "sender": "A", "receiver": "B"})
    cargo_id = create_resp.get_json()['id']
    
    response = client.delete(f'/cargo/{cargo_id}')
    assert response.status_code == 200

# Test 8: Silinen kargo tekrar sorgulandığında 404 dönüyor mu?[cite: 1]
def test_8_get_deleted_cargo(client):
    create_resp = client.post('/cargo', json={"tracking_number": "KRG-TEST8", "sender": "A", "receiver": "B"})
    cargo_id = create_resp.get_json()['id']
    client.delete(f'/cargo/{cargo_id}')
    
    response = client.get(f'/cargo/{cargo_id}')
    assert response.status_code == 404