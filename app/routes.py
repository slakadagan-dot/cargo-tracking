from flask import Blueprint, request, jsonify, Response
from datetime import datetime
import time
from .models import get_db_connection, STATUSES
from .kafka_producer import send_cargo_event
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

bp = Blueprint('cargo', __name__)

# --- PROMETHEUS METRİKLERİ ---[cite: 1]
CARGO_CREATED_COUNT = Counter('cargo_created_total', 'Total created cargos')
CARGO_DELIVERED_COUNT = Counter('cargo_delivered_total', 'Total delivered cargos')
CARGO_CANCELLED_COUNT = Counter('cargo_cancelled_total', 'Total cancelled cargos')
CARGO_STATUS_CHANGED_COUNT = Counter('cargo_status_changed_total', 'Total status changes')
API_REQUEST_COUNT = Counter('api_request_total', 'Total API requests', ['method', 'endpoint'])
API_REQUEST_DURATION = Histogram('api_request_duration', 'API request duration in seconds', ['method', 'endpoint'])

# API İsteklerinin sayısını ve hızını ölçen otomatik sistem[cite: 1]
@bp.before_request
def before_request():
    request.start_time = time.time()

@bp.after_request
def after_request(response):
    req_time = time.time() - getattr(request, 'start_time', time.time())
    API_REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    API_REQUEST_DURATION.labels(method=request.method, endpoint=request.path).observe(req_time)
    return response

# Prometheus'un metrikleri okuması için oluşturulan özel rota
@bp.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# 1. Kargo Ekleme
@bp.route('/cargo', methods=['POST'])
def create_cargo():
    data = request.get_json()
    tracking_number = data.get("tracking_number")
    
    if not tracking_number:
        return jsonify({"error": "Tracking number zorunludur"}), 400

    sender = data.get("sender")
    receiver = data.get("receiver")
    status = "CREATED"
    created_at = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO cargo (tracking_number, sender, receiver, status, created_at) VALUES (?, ?, ?, ?, ?)',
        (tracking_number, sender, receiver, status, created_at)
    )
    conn.commit()
    cargo_id = cursor.lastrowid
    conn.close()

    send_cargo_event("cargo.created", cargo_id=cargo_id, tracking_number=tracking_number)
    
    # Yeni kargo eklendiğinde sayacı 1 artırıyoruz[cite: 1]
    CARGO_CREATED_COUNT.inc()

    return jsonify({
        "id": cargo_id,
        "tracking_number": tracking_number,
        "status": status
    }), 201

# 2. Kargo Listeleme
@bp.route('/cargo', methods=['GET'])
def get_all_cargos():
    conn = get_db_connection()
    cargos = conn.execute('SELECT * FROM cargo').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in cargos]), 200

# 3. Kargo Sorgulama
@bp.route('/cargo/<int:id>', methods=['GET'])
def get_cargo(id):
    conn = get_db_connection()
    cargo = conn.execute('SELECT * FROM cargo WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if cargo is None:
        return jsonify({"error": "Kargo bulunamadı"}), 404
        
    return jsonify(dict(cargo)), 200

# 4. Kargo Durumunu Değiştirme
@bp.route('/cargo/<int:id>/status', methods=['PUT'])
def update_status(id):
    data = request.get_json()
    new_status = data.get("status")
    
    if new_status not in STATUSES:
        return jsonify({"error": "Geçersiz durum"}), 400
        
    conn = get_db_connection()
    cargo = conn.execute('SELECT * FROM cargo WHERE id = ?', (id,)).fetchone()
    
    if cargo is None:
        conn.close()
        return jsonify({"error": "Kargo bulunamadı"}), 404
        
    if cargo['status'] == 'DELIVERED':
        conn.close()
        return jsonify({"error": "Teslim edilmiş kargo güncellenemez"}), 400
        
    conn.execute('UPDATE cargo SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    
    updated_cargo = conn.execute('SELECT * FROM cargo WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    # Durumlara göre ilgili metrik sayaçlarını artırıyoruz[cite: 1]
    if new_status == 'DELIVERED':
        send_cargo_event("cargo.delivered", cargo_id=id)
        CARGO_DELIVERED_COUNT.inc() 
    elif new_status == 'CANCELLED':
        send_cargo_event("cargo.status_changed", cargo_id=id, status=new_status)
        CARGO_CANCELLED_COUNT.inc() 
    else:
        send_cargo_event("cargo.status_changed", cargo_id=id, status=new_status)
        
    CARGO_STATUS_CHANGED_COUNT.inc()
    
    return jsonify(dict(updated_cargo)), 200

# 5. Kargo Silme
@bp.route('/cargo/<int:id>', methods=['DELETE'])
def delete_cargo(id):
    conn = get_db_connection()
    cargo = conn.execute('SELECT * FROM cargo WHERE id = ?', (id,)).fetchone()
    
    if cargo is None:
        conn.close()
        return jsonify({"error": "Kargo bulunamadı"}), 404
        
    conn.execute('DELETE FROM cargo WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Kargo silindi"}), 200