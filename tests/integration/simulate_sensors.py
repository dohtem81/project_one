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
    vibration_sensor = VibrationSensor("left_front_bearing")
    temperature_sensor = TemperatureSensor("ambient")
    temperature_sensor.value = 20.0  # initial temp

    next_temp_time = now() + temperature_interval
    next_log_time = now() + log_interval

    try:
        while True:
            loop_start = now()

            # Vibration update (every 50ms)
            vibration_sensor.add_sample(random.uniform(0.0, 5.0), loop_start * 1000)  # example: 0-5 m/s^2 or arbitrary units

            # Temperature update (every 1s)
            if loop_start >= next_temp_time:
                temperature_sensor.value = temperature_sensor.value + random.uniform(-0.1, 0.1)  # simulate temp fluctuation
                next_temp_time = loop_start + temperature_interval

            # Logging (every 1s) - this is equivalent to reporting data to the cloud/server
            if loop_start >= next_log_time:
                next_log_time = loop_start + log_interval

                vibrationRecord = DataRecord(
                    data_type="vibration",
                    extra_data=vibration_sensor.serialize()
                )


                temperatureRecord = DataRecord(
                    data_type="temperature",
                    extra_data=temperature_sensor.serialize()
                )

                #report to API
                try:
                    requests.post(os.getenv("IOTGATEWAY", "http://localhost:8000/api/data"), 
                                  json=temperatureRecord.broadcast_dict())
                    requests.post(os.getenv("IOTGATEWAY", "http://localhost:8000/api/data"), 
                                  json=vibrationRecord.broadcast_dict())
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data to API: {e}", file=sys.stderr)

                # reset vibration values
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