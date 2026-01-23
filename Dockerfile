FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    pulseaudio-utils \
    ffmpeg \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /root/.interview_assistant

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS=ignore

# Expose web UI port
EXPOSE 8000

# Default command
CMD ["python", "main.py", "voice"]
