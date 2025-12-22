"""
Pytest configuration and fixtures for unit tests.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "commonpackages" / "src"))
sys.path.insert(0, str(project_root / "gateway" / "app"))
sys.path.insert(0, str(project_root / "website" / "app"))

from commonpackages.models import Base, DataRecord


@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_temperature_data():
    """Sample temperature sensor data."""
    return {
        "sensor_name": "ambient",
        "data_type": "temperature",
        "value": 25.5,
        "unit": "C",
        "timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_vibration_data():
    """Sample vibration sensor data."""
    return {
        "sensor_name": "left_front_bearing",
        "data_type": "vibration",
        "avg": 2.5,
        "peak": 5.0,
        "rms": 3.2,
        "unit": "m/s^2",
        "timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_data_record(test_session):
    """Create a sample DataRecord in the test database."""
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
    return record
