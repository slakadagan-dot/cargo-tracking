# Python tabanını kullanıyoruz
FROM python:3.12-slim

# Çalışma dizinini belirliyoruz
WORKDIR /app

# Gerekli kütüphaneleri kopyalayıp kuruyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm kodlarımızı kopyalıyoruz
COPY . .