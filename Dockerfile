# Temel imaj (Hafif)
FROM python:3.10-slim

# Sadece sistem kutuphanelerini yukle (Hizli ve Hafif)
# --no-install-recommends: Gereksiz paketleri yukleme, disk tasarrufu yap
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app