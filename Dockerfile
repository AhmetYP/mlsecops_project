# Temel imaj (Hafif Python)
FROM python:3.9-slim

# 1. Sistem kütüphanelerini ve derleyicileri yükle (Bir kere yapilacak)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Python kütüphanelerini kopyala
COPY src/requirements.txt /tmp/requirements.txt

# 3. Pip güncelle ve agir kütüphaneleri (AutoGluon vb.) yükle
# Bu islem imaj olustururken bir kez yapilir, Jenkins her seferinde yapmaz.
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# Çalisma klasörünü ayarla
WORKDIR /app