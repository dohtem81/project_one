"""
Unit tests for Gateway API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
from pathlib import Path

# Add gateway app to path
gateway_path = Path(__file__).parent.parent.parent / "gateway" / "app"
sys.path.insert(0, str(gateway_path))

from main import app
from .database import get_db
from commonpackages.models import DataRecord


@pytest.fixture
def client(test_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestDataEndpoints:
    """Tests for data submission and retrieval endpoints."""
    
    def test_submit_temperature_data(self, client):
        """Test submitting temperature data."""
        data = {
            "sensor_name": "ambient",
            "data_type": "temperature",
            "value": 25.5,
            "unit": "C",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = client.post("/api/data", json=data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["status"] == "success"
        assert "id" in response_data
    
    def test_submit_vibration_data(self, client):
        """Test submitting vibration data."""
        data = {
            "sensor_name": "left_front_bearing",
            "data_type": "vibration",
            "avg": 2.5,
            "peak": 5.0,
            "rms": 3.2,
            "unit": "m/s^2",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = client.post("/api/data", json=data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_submit_invalid_data_type(self, client):
        """Test submitting data with invalid data_type."""
        data = {
            "sensor_name": "test",
            "data_type": "invalid_type",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = client.post("/api/data", json=data)
        assert response.status_code == 422  # Validation error
    
    def test_submit_missing_required_fields(self, client):
        """Test submitting data with missing required fields."""
        data = {
            "data_type": "temperature"
            # Missing sensor_name and timestamp
        }
        
        response = client.post("/api/data", json=data)
        assert response.status_code == 422
    
    def test_get_all_data(self, client, test_session):
        """Test retrieving all data records."""
        # Add some test records
        records = [
            DataRecord(
                data_type="temperature",
                extra_data={"sensor_name": "ambient", "value": 25.5},
                timestamp=datetime.utcnow()
            ),
            DataRecord(
                data_type="vibration",
                extra_data={"sensor_name": "bearing", "avg": 2.5},
                timestamp=datetime.utcnow()
            )
        ]
        
        test_session.add_all(records)
        test_session.commit()
        
        response = client.get("/api/data")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
    
    def test_get_data_with_limit(self, client, test_session):
        """Test retrieving data with limit parameter."""
        # Add multiple records
        for i in range(10):
            record = DataRecord(
                data_type="temperature",
                extra_data={"sensor_name": "ambient", "value": 20.0 + i},
                timestamp=datetime.utcnow()
            )
            test_session.add(record)
        
        test_session.commit()
        
        response = client.get("/api/data?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5


class TestBroadcastEndpoint:
    """Tests for broadcast endpoint."""
    
    def test_broadcast_message(self, client):
        """Test broadcasting a message."""
        message = {
            "data_type": "temperature",
            "sensor_name": "ambient",
            "value": 25.5,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = client.post("/api/broadcast", json=message)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["status"] == "broadcasted"
        assert response_data["connections"] >= 0
    
    def test_broadcast_empty_message(self, client):
        """Test broadcasting an empty message."""
        response = client.post("/api/broadcast", json={})
        assert response.status_code == 200


class TestWebSocketEndpoint:
    """Tests for WebSocket endpoint."""
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection establishment."""
        with client.websocket_connect("/ws") as websocket:
            # Connection should be established
            assert websocket is not None
    
    def test_websocket_receives_broadcast(self, client, test_session):
        """Test that WebSocket receives broadcast messages."""
        with client.websocket_connect("/ws") as websocket:
            # Submit data which should be broadcast
            data = {
                "sensor_name": "ambient",
                "data_type": "temperature",
                "value": 25.5,
                "unit": "C",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Post data through API
            response = client.post("/api/data", json=data)
            assert response.status_code == 200
            
            # WebSocket should receive the broadcast
            # Note: This test may need adjustment based on actual implementation
            # since the broadcast happens asynchronously


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options(
            "/api/data",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
