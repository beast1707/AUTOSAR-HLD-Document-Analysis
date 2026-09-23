FROM python:3.12-slim

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

CMD ["python", "backend/main.py"]
