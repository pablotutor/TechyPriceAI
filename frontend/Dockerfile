# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app/frontend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el frontend
COPY . .

EXPOSE 8501

# Comando para arrancar Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]