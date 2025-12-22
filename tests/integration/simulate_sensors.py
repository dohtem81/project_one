import time
import random
import json
import argparse
import sys
from typing import Optional
from commonpackages.sensor import TemperatureSensor, VibrationSensor
from commonpackages.models import DataRecord
import os
import requests

#!/usr/bin/env python3
"""
tests/integration/simulate_sensors.py

Simulate sensors:
 - vibration sensor updates every 50ms
 - temperature sensor updates every 1s

Prints JSON lines with timestamp, sensor name and value.
"""



def now() -> float:
    return time.time()


def iso_ts(t: Optional[float] = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t or now())) + f".{int(((t or now())%1)*1000):03d}Z"


def simulate_loop(duration: Optional[float] = None) -> None:
    start_time = now()
    end_time = start_time + duration if duration is not None else None

    vibration_interval = 0.05  # 50 ms
    temperature_interval = 1.0  # 1 s
    log_interval = 1.0  # 1 s
    vibration_sensors = [VibrationSensor("left_front_bearing"), 
                         VibrationSensor("right_front_bearing"), 
                         VibrationSensor("left_rear_bearing"), 
                         VibrationSensor("right_rear_bearing")]
    temperature_sensors = [TemperatureSensor("ambient"), 
                           TemperatureSensor("left_front_bearing"), 
                           TemperatureSensor("right_front_bearing"), 
                           TemperatureSensor("left_rear_bearing"), 
                           TemperatureSensor("right_rear_bearing")]
    # for each temperature sensor, set initial value
    for sensor in temperature_sensors:
        sensor.value = 25.0 + random.uniform(-5.0, 5.0)  # initial temp between 20-30C

    next_temp_time = now() + temperature_interval
    next_log_time = now() + log_interval

    try:
        while True:
            loop_start = now()

            # Vibration update (every 50ms)
            # for each vibration sensor, add a random sample
            for vibration_sensor in vibration_sensors:
                vibration_sensor.add_sample(random.uniform(0.0, 5.0), loop_start * 1000)  # example: 0-5 m/s^2 or arbitrary units

            # Temperature update (every 1s)
            if loop_start >= next_temp_time:
                # for each temp sensor, slightly vary the temperature
                for temperature_sensor in temperature_sensors:
                    temperature_sensor.value = temperature_sensor.value + random.uniform(-0.1, 0.1)  # simulate temp fluctuation
                next_temp_time = loop_start + temperature_interval

            # Logging (every 1s) - this is equivalent to reporting data to the cloud/server
            if loop_start >= next_log_time:
                next_log_time = loop_start + log_interval

                #report to API
                try:
                    #for each temperature sensor as separate record
                    for sensor in temperature_sensors:
                        temperatureRecord = DataRecord(
                            data_type="temperature",
                            extra_data=sensor.serialize()
                        )
                        requests.post(os.getenv("IOTGATEWAY", "http://localhost:8000/api/data"), 
                                  json=temperatureRecord.broadcast_dict())
                    # each vibration sensor as separate record
                    for sensor in vibration_sensors:
                        sensorRecord = DataRecord(
                            data_type="vibration",
                            extra_data=sensor.serialize()
                        )
                        requests.post(os.getenv("IOTGATEWAY", "http://localhost:8000/api/data"), 
                                      json=sensorRecord.broadcast_dict())
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data to API: {e}", file=sys.stderr)

                # reset vibration values
                for vibration_sensor in vibration_sensors:
                    vibration_sensor.reset()

            # exit if duration reached
            if end_time is not None and loop_start >= end_time:
                break

            # sleep to maintain ~50ms loop
            elapsed = now() - loop_start
            to_sleep = vibration_interval - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)
            else:
                # if we're behind schedule, yield briefly to avoid busy loop
                time.sleep(0)
    except KeyboardInterrupt:
        pass


def parse_args():
    p = argparse.ArgumentParser(description="Simulate vibration (50ms) and temperature (1s) sensors.")
    p.add_argument("--duration", "-d", type=float, default=None, help="Run duration in seconds (default: run until interrupted)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    simulate_loop(duration=args.duration)