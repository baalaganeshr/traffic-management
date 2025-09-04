# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only essential requirements for the gamified app
COPY requirements.txt .

# Install only core dependencies needed for the gamified dashboard
RUN pip install --no-cache-dir \
    streamlit==1.46.0 \
    pandas==2.2.3 \
    numpy \
    plotly==6.2.0

# Copy the entire application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the professional dashboard
# Run the application
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]