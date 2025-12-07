FROM python:3.11-slim

WORKDIR /app

# Copy and install shared objects package first
COPY ../sharedobjects ./sharedobjects
RUN pip install -e ./sharedobjects

# Install dependencies
COPY ./gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./gateway ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
