FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy your full app folder
COPY . /app

EXPOSE 5000

# Start Flask app
CMD ["python", "chat.py"]
