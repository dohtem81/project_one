FROM python:3.11-slim

WORKDIR /app

# Copy and install shared objects package first
COPY ../sharedobjects /app/sharedobjects

# Debug: List what was copied
RUN ls -la /app/sharedobjects

RUN pip install -e /app/sharedobjects

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy consumer code
COPY . .

CMD ["python", "consumer.py"]
