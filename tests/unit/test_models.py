"""
Unit tests for database models.
"""
import pytest
from datetime import datetime, timedelta
from commonpackages.models import DataRecord


class TestDataRecord:
    """Tests for DataRecord model."""
    
    def test_create_temperature_record(self, test_session):
        """Test creating a temperature data record."""
        record = DataRecord(
            data_type="temperature",
            extra_data={
                "sensor_name": "ambient",
                "value": 25.5,
                "unit": "C"
            },
            timestamp=datetime.utcnow()
        )
        
        test_session.add(record)
        test_session.commit()
        test_session.refresh(record)
        
        assert record.id is not None
        assert record.data_type == "temperature"
        assert record.extra_data["sensor_name"] == "ambient"
        assert record.extra_data["value"] == 25.5
        assert record.extra_data["unit"] == "C"
        assert isinstance(record.timestamp, datetime)
    
    def test_create_vibration_record(self, test_session):
        """Test creating a vibration data record."""
        record = DataRecord(
            data_type="vibration",
            extra_data={
                "sensor_name": "left_front_bearing",
                "avg": 2.5,
                "peak": 5.0,
                "rms": 3.2,
                "unit": "m/s^2"
            },
            timestamp=datetime.utcnow()
        )
        
        test_session.add(record)
        test_session.commit()
        test_session.refresh(record)
        
        assert record.id is not None
        assert record.data_type == "vibration"
        assert record.extra_data["sensor_name"] == "left_front_bearing"
        assert record.extra_data["avg"] == 2.5
        assert record.extra_data["peak"] == 5.0
        assert record.extra_data["rms"] == 3.2
    
    def test_query_by_data_type(self, test_session):
        """Test querying records by data type."""
        # Create multiple records
        temp_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 25.5},
            timestamp=datetime.utcnow()
        )
        vib_record = DataRecord(
            data_type="vibration",
            extra_data={"sensor_name": "bearing", "avg": 2.5},
            timestamp=datetime.utcnow()
        )
        
        test_session.add(temp_record)
        test_session.add(vib_record)
        test_session.commit()
        
        # Query temperature records
        temp_results = test_session.query(DataRecord).filter(
            DataRecord.data_type == "temperature"
        ).all()
        
        assert len(temp_results) == 1
        assert temp_results[0].data_type == "temperature"
    
    def test_query_by_sensor_name(self, test_session):
        """Test querying records by sensor name using JSON field."""
        # Create records with different sensor names
        records_data = [
            {"sensor": "ambient", "value": 25.5},
            {"sensor": "left_front_bearing", "value": 30.0},
            {"sensor": "ambient", "value": 26.0}
        ]
        
        for data in records_data:
            record = DataRecord(
                data_type="temperature",
                extra_data={"sensor_name": data["sensor"], "value": data["value"]},
                timestamp=datetime.utcnow()
            )
            test_session.add(record)
        
        test_session.commit()
        
        # Query ambient sensor records
        ambient_results = test_session.query(DataRecord).filter(
            DataRecord.extra_data["sensor_name"].astext == "ambient"
        ).all()
        
        assert len(ambient_results) == 2
        for record in ambient_results:
            assert record.extra_data["sensor_name"] == "ambient"
    
    def test_query_recent_records(self, test_session):
        """Test querying records from the last N minutes."""
        now = datetime.utcnow()
        
        # Create records with different timestamps
        old_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 20.0},
            timestamp=now - timedelta(minutes=30)
        )
        recent_record = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 25.0},
            timestamp=now - timedelta(minutes=5)
        )
        
        test_session.add(old_record)
        test_session.add(recent_record)
        test_session.commit()
        
        # Query records from last 15 minutes
        cutoff_time = now - timedelta(minutes=15)
        recent_results = test_session.query(DataRecord).filter(
            DataRecord.timestamp >= cutoff_time
        ).all()
        
        assert len(recent_results) == 1
        assert recent_results[0].extra_data["value"] == 25.0
    
    def test_broadcast_dict(self, sample_data_record):
        """Test broadcast_dict serialization method."""
        broadcast_data = sample_data_record.broadcast_dict()
        
        assert "data_type" in broadcast_data
        assert "sensor_name" in broadcast_data
        assert "value" in broadcast_data
        assert "unit" in broadcast_data
        assert "timestamp" in broadcast_data
        
        # Check that timestamp is ISO formatted string
        assert isinstance(broadcast_data["timestamp"], str)
        datetime.fromisoformat(broadcast_data["timestamp"].replace("Z", "+00:00"))
    
    def test_order_by_timestamp(self, test_session):
        """Test ordering records by timestamp."""
        now = datetime.utcnow()
        
        # Create records in non-chronological order
        record2 = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 25.0},
            timestamp=now - timedelta(seconds=30)
        )
        record1 = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 20.0},
            timestamp=now - timedelta(seconds=60)
        )
        record3 = DataRecord(
            data_type="temperature",
            extra_data={"sensor_name": "ambient", "value": 30.0},
            timestamp=now
        )
        
        test_session.add_all([record2, record1, record3])
        test_session.commit()
        
        # Query ordered by timestamp
        ordered_results = test_session.query(DataRecord).order_by(
            DataRecord.timestamp.asc()
        ).all()
        
        assert len(ordered_results) == 3
        assert ordered_results[0].extra_data["value"] == 20.0
        assert ordered_results[1].extra_data["value"] == 25.0
        assert ordered_results[2].extra_data["value"] == 30.0
    
    def test_delete_record(self, test_session, sample_data_record):
        """Test deleting a data record."""
        record_id = sample_data_record.id
        
        # Verify record exists
        assert test_session.query(DataRecord).filter(
            DataRecord.id == record_id
        ).first() is not None
        
        # Delete record
        test_session.delete(sample_data_record)
        test_session.commit()
        
        # Verify record is deleted
        assert test_session.query(DataRecord).filter(
            DataRecord.id == record_id
        ).first() is None
