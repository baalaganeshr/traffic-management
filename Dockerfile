# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies (removed unnecessary graphics libs for web deployment)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./requirements.txt

# Install Python dependencies with upgraded pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port 8501 (Render will use $PORT at runtime, but Docker needs a default)
EXPOSE 8501

# Make start script executable
RUN chmod +x start.sh

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Use shell form to properly handle $PORT environment variable
CMD bash -c "PORT=\${PORT:-8501} && echo 'Starting on port:' \$PORT && streamlit run frontend/app_unified_improved.py --server.port=\$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false"
