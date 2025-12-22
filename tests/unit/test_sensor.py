"""
Unit tests for sensor classes.
"""
import pytest
from sensor import TemperatureSensor, VibrationSensor


class TestTemperatureSensor:
    """Tests for TemperatureSensor class."""
    
    def test_initialization(self):
        """Test sensor initialization with default values."""
        sensor = TemperatureSensor(name="ambient", min_value=10.0, max_value=50.0)
        assert sensor.name == "ambient"
        assert sensor.min_value == 10.0
        assert sensor.max_value == 50.0
        assert sensor.value is None
        assert sensor.previous_value is None
    
    def test_initialization_with_initial_value(self):
        """Test sensor initialization with initial value."""
        sensor = TemperatureSensor(
            name="ambient",
            min_value=10.0,
            max_value=50.0,
            initial_value=25.0
        )
        assert sensor.value == 25.0
        assert sensor.previous_value is None
    
    def test_generate_value_within_range(self):
        """Test that generated values stay within min/max range."""
        sensor = TemperatureSensor(name="test", min_value=20.0, max_value=30.0)
        
        for _ in range(100):
            value = sensor.generate_value()
            assert 20.0 <= value <= 30.0
    
    def test_generate_value_updates_previous(self):
        """Test that generate_value updates previous_value."""
        sensor = TemperatureSensor(name="test", min_value=20.0, max_value=30.0)
        
        first_value = sensor.generate_value()
        assert sensor.previous_value is None
        
        second_value = sensor.generate_value()
        assert sensor.previous_value == first_value
        assert sensor.value == second_value
    
    def test_serialize(self):
        """Test sensor serialization."""
        sensor = TemperatureSensor(
            name="ambient",
            min_value=10.0,
            max_value=50.0,
            initial_value=25.5
        )
        
        data = sensor.serialize()
        assert data["sensor_name"] == "ambient"
        assert data["data_type"] == "temperature"
        assert data["value"] == 25.5
        assert data["unit"] == "C"
        assert "timestamp" in data
    
    def test_serialize_without_value(self):
        """Test serialization when no value has been generated."""
        sensor = TemperatureSensor(name="test", min_value=10.0, max_value=50.0)
        
        data = sensor.serialize()
        assert data["value"] is None


class TestVibrationSensor:
    """Tests for VibrationSensor class."""
    
    def test_initialization(self):
        """Test vibration sensor initialization."""
        sensor = VibrationSensor(
            name="left_front_bearing",
            min_value=0.0,
            max_value=10.0
        )
        assert sensor.name == "left_front_bearing"
        assert sensor.min_value == 0.0
        assert sensor.max_value == 10.0
        assert sensor.avg == 0.0
        assert sensor.peak == 0.0
        assert sensor.rms == 0.0
        assert sensor.count == 0
    
    def test_add_sample_single(self):
        """Test adding a single sample."""
        sensor = VibrationSensor(name="test", min_value=0.0, max_value=10.0)
        
        sensor.add_sample(5.0)
        
        assert sensor.avg == 5.0
        assert sensor.peak == 5.0
        assert sensor.rms == 5.0
        assert sensor.count == 1
    
    def test_add_sample_multiple(self):
        """Test adding multiple samples."""
        sensor = VibrationSensor(name="test", min_value=0.0, max_value=10.0)
        
        samples = [2.0, 4.0, 6.0, 8.0]
        for sample in samples:
            sensor.add_sample(sample)
        
        # Check count
        assert sensor.count == 4
        
        # Check average: (2+4+6+8)/4 = 5.0
        assert sensor.avg == 5.0
        
        # Check peak: max(2,4,6,8) = 8.0
        assert sensor.peak == 8.0
        
        # Check RMS: sqrt((4+16+36+64)/4) = sqrt(30) ≈ 5.477
        assert abs(sensor.rms - 5.477) < 0.01
    
    def test_reset(self):
        """Test sensor reset functionality."""
        sensor = VibrationSensor(name="test", min_value=0.0, max_value=10.0)
        
        # Add some samples
        sensor.add_sample(5.0)
        sensor.add_sample(10.0)
        
        # Reset
        sensor.reset()
        
        assert sensor.avg == 0.0
        assert sensor.peak == 0.0
        assert sensor.rms == 0.0
        assert sensor.count == 0
    
    def test_serialize(self):
        """Test vibration sensor serialization."""
        sensor = VibrationSensor(
            name="left_front_bearing",
            min_value=0.0,
            max_value=10.0
        )
        
        # Add samples
        sensor.add_sample(2.0)
        sensor.add_sample(4.0)
        sensor.add_sample(6.0)
        
        data = sensor.serialize()
        
        assert data["sensor_name"] == "left_front_bearing"
        assert data["data_type"] == "vibration"
        assert data["avg"] == 4.0
        assert data["peak"] == 6.0
        assert abs(data["rms"] - 4.32) < 0.01
        assert data["unit"] == "m/s^2"
        assert "timestamp" in data
    
    def test_serialize_no_samples(self):
        """Test serialization with no samples."""
        sensor = VibrationSensor(name="test", min_value=0.0, max_value=10.0)
        
        data = sensor.serialize()
        
        assert data["avg"] == 0.0
        assert data["peak"] == 0.0
        assert data["rms"] == 0.0
    
    def test_generate_value_adds_samples(self):
        """Test that generate_value adds samples."""
        sensor = VibrationSensor(name="test", min_value=0.0, max_value=10.0)
        
        # Generate some values
        for _ in range(10):
            sensor.generate_value()
        
        assert sensor.count == 10
        assert 0.0 <= sensor.avg <= 10.0
        assert 0.0 <= sensor.peak <= 10.0
        assert 0.0 <= sensor.rms <= 10.0
