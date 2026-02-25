# backend/Dockerfile
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# 🚨 LA MAGIA AQUÍ: Instalamos la librería C++ que necesita LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero el requirements (para aprovechar la caché de Docker)
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del backend y la carpeta models
COPY . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]