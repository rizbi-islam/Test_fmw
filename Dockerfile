# ─────────────────────────────────────────────────────────────
# KWAF — Dockerfile
# Usage:
#   docker build -t kwaf .
#   docker run kwaf python run.py --headless
#   docker run -p 8501:8501 kwaf streamlit run ui/app.py --server.address=0.0.0.0
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

# System dependencies for Playwright/Chromium
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    libglib2.0-0 libnss3 libfontconfig1 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 \
    libxrender1 libxss1 libxtst6 libpango-1.0-0 libpangocairo-1.0-0 \
    libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libgbm1 libasound2 \
    fonts-liberation xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy project files
COPY . .

# Create runtime directories
RUN mkdir -p assets/screenshots assets/data reports/output logs data

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py", "--headless"]
