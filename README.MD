# Project One - IoT Data Collection Platform

A real-time IoT data collection and monitoring platform built with FastAPI, PostgreSQL, RabbitMQ, and WebSockets. The system enables data ingestion from IoT sensors, real-time processing through message queues, and live visualization through a web dashboard.

## 🏗️ Architecture

The platform consists of several microservices orchestrated with Docker Compose:

- **Gateway Service**: FastAPI-based REST API and WebSocket server for data ingestion
- **IoT Consumer**: Background worker that processes messages from RabbitMQ queue
- **Website**: Real-time dashboard for monitoring and visualizing IoT data
- **PostgreSQL**: Primary database for persistent data storage
- **RabbitMQ**: Message broker for asynchronous processing
- **pgAdmin**: Database administration interface
- **Swagger UI**: API documentation interface

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project_one
```

### 2. Environment Configuration

Create a `.env` file in the project root (optional - defaults are provided):

```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=project_one_db

# RabbitMQ
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
```

### 3. Start All Services

```bash
docker-compose up -d
```

### 4. Access the Applications

- **Gateway API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8080
- **Website Dashboard**: http://localhost:3000
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **pgAdmin**: http://localhost:5050 (admin@admin.com/admin)

## 📦 Project Structure

```
project_one/
├── commonpackages/         # Shared models and utilities
│   ├── src/
│   │   ├── models.py      # SQLAlchemy database models
│   │   └── sensor.py      # Sensor utilities
│   └── pyproject.toml
├── gateway/               # API Gateway service
│   ├── app/
│   │   ├── main.py       # FastAPI application
│   │   ├── database.py   # Database configuration
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── models.py     # Data models
│   │   └── websocket_manager.py
│   ├── Dockerfile
│   └── requirements.txt
├── iotconsumer/          # Message queue consumer
│   ├── consumer.py       # RabbitMQ consumer
│   ├── Dockerfile
│   └── requirements.txt
├── website/              # Web dashboard
│   ├── app/
│   │   ├── main.py      # Dashboard FastAPI app
│   │   ├── static/      # CSS, JS files
│   │   └── templates/   # HTML templates
│   ├── Dockerfile
│   └── requirements.txt
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docker-compose.yml   # Main compose file
└── pytest.ini          # Pytest configuration
```

## 🔧 API Endpoints

### Gateway Service (Port 8000)

#### POST `/data`
Submit sensor data to the system.

**Request Body:**
```json
{
  "data_type": "temperature",
  "extra_data": {
    "value": 22.5,
    "unit": "celsius"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "data_type": "temperature",
  "extra_data": {
    "value": 22.5,
    "unit": "celsius"
  },
  "timestamp": "2025-12-28T10:30:00"
}
```

#### GET `/data`
Retrieve all data records.

**Query Parameters:**
- `skip`: Offset for pagination (default: 0)
- `limit`: Number of records to return (default: 100)

#### WebSocket `/ws`
Real-time data streaming endpoint. Connect to receive live updates when new data is ingested.

## 🧪 Testing

### Run Unit Tests

```bash
# Using Docker
docker-compose -f docker-compose-test.yml up --build

# Local development
pytest tests/unit/
```

### Run Integration Tests

```bash
pytest tests/integration/
```

### Test Coverage

```bash
pytest --cov=commonpackages --cov=gateway --cov=website --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in your browser.

## 🛠️ Development

### Local Setup

1. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**

```bash
# Install common packages
pip install -e commonpackages/

# Install service dependencies
pip install -r gateway/requirements.txt
pip install -r iotconsumer/requirements.txt
pip install -r website/requirements.txt
```

3. **Run Services Locally**

```bash
# Gateway
cd gateway
uvicorn app.main:app --reload --port 8000

# Website
cd website
uvicorn app.main:app --reload --port 3000

# Consumer
cd iotconsumer
python consumer.py
```

### Database Migrations

The application automatically creates tables on startup using SQLAlchemy's `create_all()`. For production, consider using Alembic for proper migrations.

## 🔍 Monitoring

### RabbitMQ Management

Access the RabbitMQ management console at http://localhost:15672 to:
- Monitor queue depth
- View message rates
- Inspect connections and channels

### Database Administration

Use pgAdmin at http://localhost:5050 to:
- Query data records
- Monitor database performance
- Manage database schema

### Application Logs

View service logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f iotconsumer
docker-compose logs -f website
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# View logs
docker-compose logs -f [service-name]

# Access service shell
docker exec -it project_one_gateway /bin/bash

# Remove all data (volumes)
docker-compose down -v
```

## 🌐 WebSocket Client Example

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from WebSocket');
};
```

## 📊 Data Flow

1. **Data Ingestion**: IoT sensors or clients POST data to the Gateway API
2. **Storage**: Data is stored in PostgreSQL for persistence
3. **Queue Publishing**: Gateway publishes messages to RabbitMQ
4. **Processing**: IoT Consumer picks up messages and processes them
5. **Real-time Updates**: WebSocket broadcasts updates to connected clients
6. **Visualization**: Website dashboard displays real-time and historical data

## 🔒 Security Considerations

For production deployment:

- Change default passwords in `.env` file
- Configure CORS to allow only specific origins
- Use HTTPS/WSS for encrypted connections
- Implement authentication and authorization
- Use secrets management (e.g., Docker Secrets, HashiCorp Vault)
- Enable PostgreSQL SSL connections
- Configure RabbitMQ with proper user permissions

## 🚧 Known Limitations

- No authentication/authorization implemented
- CORS is set to allow all origins (development only)
- Database migrations are not versioned (using `create_all()`)
- No rate limiting on API endpoints
- Error handling could be more comprehensive

## 📝 License

[Add your license information here]

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

[Add your contact information here]

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- RabbitMQ for reliable message queuing
- PostgreSQL for robust data storage
- Docker for containerization simplicity
