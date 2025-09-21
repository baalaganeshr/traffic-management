# Minimal Dockerfile that forces our production system
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# FORCE: Use run.py which handles PORT environment variable
CMD ["python", "run.py"]
