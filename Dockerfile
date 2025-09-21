# Use Python 3.11 slim image
FROM python:3.11-slim
# Set working directory
WORKDIR /app
# Install system dependencies for pygame and graphics
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libsmpeg-dev \
    libportmidi-dev \
    libavformat-dev \
    libswscale-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements and install Python dependencies
COPY requirements.txt ./requirements.txt
# Install Python dependencies with upgraded pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
# Copy the entire application
COPY . .
# Expose port (will be set by $PORT environment variable)
EXPOSE $PORT
# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV SDL_VIDEODRIVER=dummy
ENV PYGAME_HIDE_SUPPORT_PROMPT=1
# Temporary debug command to list frontend directory
CMD ls -l frontend
