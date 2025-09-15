FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: emergentintegrations requires special index, but for deployment we can skip it
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Installing without emergentintegrations..." && \
     pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 motor==3.3.2 pydantic==2.5.0 python-multipart==0.0.6 pymongo==4.6.0 pandas==2.1.4 openpyxl==3.1.2 pytz==2023.3 redis==5.0.1 aioredis==2.0.1 elasticsearch==8.11.1 aioelasticsearch==0.7.0 slowapi==0.1.9 python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 psutil==5.9.6 numpy==1.24.4 matplotlib==3.7.5 seaborn==0.12.2 scipy==1.11.4 websockets==12.0 python-socketio==5.10.0 aiofiles==23.2.1 pillow==10.1.0 opencv-python==4.8.1.78 scikit-learn==1.3.2 requests==2.31.0 pycryptodome==3.19.0 qrcode==7.4.2 reportlab==4.0.7)

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]