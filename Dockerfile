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

# Expose port (Render will use $PORT at runtime, but Docker needs a default)
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Copy and make start script executable
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Run the professional dashboard with dynamic port using start script
CMD ["./start.sh"]
