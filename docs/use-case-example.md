# Use Case Example

## Scenario

A machine sends temperature and vibration data. The system stores it and makes it queryable.

## End-to-End Steps

1. Device sends payload to gateway.
2. Gateway validates payload and queues message.
3. Consumer reads queue message.
4. Consumer writes a `DataRecord` row to Postgres.
5. Client reads latest data through `GET /api/data`.

## Sample Request

```bash
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{
    "value": 22.7,
    "data_type": "temperature",
    "extra_data": {"sensor_id": "ambient-01", "unit": "C"}
  }'
```

Expected response:

```json
{"status":"accepted","message":"Data queued for processing"}
```

## Read Stored Data

```bash
curl "http://localhost:8000/api/data?limit=10"
```

## Optional Sensor Simulation

Use built-in simulator:

```bash
python tests/integration/simulate_sensors.py --duration 10
```
