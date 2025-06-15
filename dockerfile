# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc

# Copy requirements and install

EXPOSE 8050

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY . .

# Set environment variable to avoid bytecode files
ENV PYTHONDONTWRITEBYTECODE=1

# Set environment variable to unbuffer stdout
ENV PYTHONUNBUFFERED=1

# Tell App Runner how to start the app
CMD ["python", "app.py"]
