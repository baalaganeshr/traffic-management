# Minimal Dockerfile that forces our production system
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# FORCE: Use our main.py entry point
CMD ["python", "main.py"]
