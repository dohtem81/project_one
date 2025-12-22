FROM python:3.11-slim

WORKDIR /app

# Copy and install shared objects package first
COPY ./commonpackages /app/commonpackages
RUN pip install -e /app/commonpackages

# Install dependencies
COPY ./website/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./website .

EXPOSE 3000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]