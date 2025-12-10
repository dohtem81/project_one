import json
from abc import ABC, abstractmethod
import time

class Sensor:
    def __init__(self, name, sensor_type):
        self.name = name
        self.sensor_type = sensor_type
        self.unit = None

    @abstractmethod
    def read_value(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def serialize(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def serialzie(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    

class TemperatureSensor(Sensor):
    @property
    def value(self):
        return getattr(self, "_value", None)

    @value.setter
    def value(self, new_value):
        self._prev_value = getattr(self, "_value", None)
        self._value = new_value

    @property
    def prev_value(self):
        return getattr(self, "_prev_value", None)
    
    def __init__(self, name):
        super().__init__(name, "temperature")

    def read_value(self):
        return getattr(self, "_value", None)
    
    def serialize(self):
        return {
            "name": self.name,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "prev_value": self.prev_value
        }
  
    def toString(self):
        data = {
            "name": self.name,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "prev_value": self.prev_value,
            "unit": "Celsius"
        }
        return json.dumps(data)

class VibrationSensor(Sensor):
    def __init__(self, name):
        super().__init__(name, "vibration")
        self._samples: list[float] = []
        self._last_report_ts: float | None = None
        self.reset()

    def add_sample(self, value: float, timestamp_ms: float):
        self._samples.append(value)
        # store the timestamp of the last sample to use the parameter
        self._last_report_ts = timestamp_ms
        self.recalculate_aggregates()
    
    def recalculate_aggregates(self):
        count = len(self._samples)
        if count:
            self._peak = max(self._samples, key=abs)
            self._avg = sum(self._samples) / count
            self._rms = (sum(s * s for s in self._samples) / count) ** 0.5
        else:
            self._peak = None
            self._avg = None
            self._rms = None

    def read_value(self):
        return getattr(self, "_avg", None)

    @property
    def value(self):
        return self._samples[-1] if self._samples else None

    def serialize(self):
        return {
            "name": self.name,
            "timestamp": self._last_report_ts,
            "sensor_type": self.sensor_type,
            "avg": self._avg,
            "peak": self._peak,
            "rms": self._rms,
            "count": len(self._samples),
            "unit": "m/s^2"
        }
    
    def toString(self):
         return json.dumps({
            "nm": self.name,
            "ts": self._last_report_ts,
            "tp": self.sensor_type,
            "av": self._avg,
            "pk": self._peak,
            "rms": self._rms,
            "cnt": len(self._samples)
        })   
    def reset(self):
        """Clear accumulated vibration metrics and samples."""
        self._samples.clear()
        self._last_report_ts = None
        self._peak = None
        self._avg = None
        self._rms = None