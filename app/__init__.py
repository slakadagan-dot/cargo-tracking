from flask import Flask
from .models import init_db

def create_app():
    app = Flask(__name__)
    
    # Sunucu başlarken veritabanı tablosunu oluştur
    init_db()
    
    # Rotalarımızı uygulamaya tanıtıyoruz
    from .routes import bp
    app.register_blueprint(bp)
    
    return app