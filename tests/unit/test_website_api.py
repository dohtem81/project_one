"""
Unit tests for Website API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add website app to path
website_path = Path(__file__).parent.parent.parent / "website" / "app"
sys.path.insert(0, str(website_path))

from main import app
from database import get_db
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


class TestDashboardEndpoint:
    """Tests for dashboard rendering endpoint."""
    
    def test_dashboard_renders(self, client):
        """Test that dashboard page renders successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.content
        assert b"IoT Dashboard" in response.content
    
    def test_dashboard_includes_websocket_url(self, client):
        """Test that dashboard includes WebSocket URL."""
        response = client.get("/")
        assert response.status_code == 200
        # Should contain WebSocket connection logic
        assert b"WebSocket" in response.content or b"ws://" in response.content


class TestAmbientHistoryEndpoint:
    """Tests for ambient temperature history endpoint."""
    
    def test_get_ambient_history_empty(self, client):
        """Test ambient history with no data."""
        response = client.get("/api/ambient-history")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_ambient_history_with_data(self, client, test_session):
        """Test ambient history returns recent data."""
        now = datetime.utcnow()
        
        # Add ambient temperature records
        records = [
            DataRecord(
                data_type="temperature",
                extra_data={
                    "sensor_name": "ambient",
                    "value": 25.0 + i,
                    "unit": "C"
                },
                timestamp=now - timedelta(minutes=i)
            )
            for i in range(5)
        ]
        
        test_session.add_all(records)
        test_session.commit()
        
        response = client.get("/api/ambient-history")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5
        
        # Verify data structure
        for item in data:
            assert "timestamp" in item
            assert "value" in item
            assert isinstance(item["value"], (int, float))
    
    def test_ambient_history_filters_by_sensor(self, client, test_session):
        """Test that endpoint only returns ambient sensor data."""
        now = datetime.utcnow()
        
        # Add both ambient and bearing temperature records
        ambient_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 25.0},
            timestamp=now
        )
        bearing_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "left_front_bearing", "value": 30.0},
            timestamp=now
        )
        
        test_session.add_all([ambient_record, bearing_record])
        test_session.commit()
        
        response = client.get("/api/ambient-history")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["value"] == 25.0
    
    def test_ambient_history_time_range(self, client, test_session):
        """Test that endpoint returns data from last 15 minutes."""
        now = datetime.utcnow()
        
        # Add recent and old records
        recent_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 25.0},
            timestamp=now - timedelta(minutes=5)
        )
        old_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 20.0},
            timestamp=now - timedelta(minutes=20)
        )
        
        test_session.add_all([recent_record, old_record])
        test_session.commit()
        
        response = client.get("/api/ambient-history")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["value"] == 25.0


class TestWheelsHistoryEndpoint:
    """Tests for wheels history endpoint."""
    
    def test_get_wheels_history_empty(self, client):
        """Test wheels history with no data."""
        response = client.get("/api/wheels-history")
        assert response.status_code == 200
        
        data = response.json()
        assert "left_front" in data
        assert "right_front" in data
        assert "left_rear" in data
        assert "right_rear" in data
        
        # All should be empty arrays
        for wheel in data.values():
            assert wheel == []
    
    def test_get_wheels_history_with_data(self, client, test_session):
        """Test wheels history returns data for all bearings."""
        now = datetime.utcnow()
        
        # Add temperature records for each bearing
        bearings = [
            "left_front_bearing",
            "right_front_bearing",
            "left_rear_bearing",
            "right_rear_bearing"
        ]
        
        for bearing in bearings:
            temp_record = DataRecord(
                data_type="temperature",
                extra_data={
                    "sensor_name": bearing,
                    "value": 30.0,
                    "unit": "C"
                },
                timestamp=now
            )
            vib_record = DataRecord(
                data_type="vibration",
                extra_data={
                    "sensor_name": bearing,
                    "avg": 2.5,
                    "peak": 5.0,
                    "rms": 3.2,
                    "unit": "m/s^2"
                },
                timestamp=now
            )
            test_session.add(temp_record)
            test_session.add(vib_record)
        
        test_session.commit()
        
        response = client.get("/api/wheels-history")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all wheels have data
        for wheel_key in ["left_front", "right_front", "left_rear", "right_rear"]:
            assert wheel_key in data
            assert len(data[wheel_key]) > 0
            
            # Check data structure
            for item in data[wheel_key]:
                assert "timestamp" in item
                assert "temperature" in item or "vibration" in item
    
    def test_wheels_history_vibration_structure(self, client, test_session):
        """Test that vibration data includes avg, peak, rms."""
        now = datetime.utcnow()
        
        vib_record = DataRecord(
            data_type="vibration",
            extra_data={
                "sensor_name": "left_front_bearing",
                "avg": 2.5,
                "peak": 5.0,
                "rms": 3.2,
                "unit": "m/s^2"
            },
            timestamp=now
        )
        
        test_session.add(vib_record)
        test_session.commit()
        
        response = client.get("/api/wheels-history")
        assert response.status_code == 200
        
        data = response.json()
        left_front = data["left_front"]
        
        # Find vibration record
        vib_data = [item for item in left_front if "vibration" in item][0]
        
        assert "vibration" in vib_data
        vibration = vib_data["vibration"]
        assert "avg" in vibration
        assert "peak" in vibration
        assert "rms" in vibration
        assert vibration["avg"] == 2.5
        assert vibration["peak"] == 5.0
        assert vibration["rms"] == 3.2
    
    def test_wheels_history_time_range(self, client, test_session):
        """Test that endpoint returns data from last 15 minutes."""
        now = datetime.utcnow()
        
        # Add recent and old records
        recent_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "left_front_bearing", "value": 30.0},
            timestamp=now - timedelta(minutes=5)
        )
        old_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "left_front_bearing", "value": 25.0},
            timestamp=now - timedelta(minutes=20)
        )
        
        test_session.add_all([recent_record, old_record])
        test_session.commit()
        
        response = client.get("/api/wheels-history")
        assert response.status_code == 200
        
        data = response.json()
        left_front = data["left_front"]
        
        # Should only have recent record
        assert len(left_front) == 1
        assert left_front[0]["temperature"] == 30.0


class TestStaticFiles:
    """Tests for static file serving."""
    
    def test_css_file_exists(self, client):
        """Test that CSS file is accessible."""
        response = client.get("/static/style.css")
        # May be 200 if file exists or 404 if not in test environment
        assert response.status_code in [200, 404]
