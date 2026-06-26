# # Use Python 3.11 slim image
# FROM python:3.11-slim

# # Prevent Python from writing .pyc files
# ENV PYTHONDONTWRITEBYTECODE=1

# # Show logs immediately
# ENV PYTHONUNBUFFERED=1

# # Set working directory
# WORKDIR /app

# # Copy requirements first (better Docker cache)
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project files
# COPY . .

# # Expose FastAPI port
# EXPOSE 8000

# # Start FastAPI
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy from backend subfolder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]