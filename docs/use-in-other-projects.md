# Use In Other Projects

## Reuse Goal

Use `packages/commonpackages` as a shared Python package for models and sensor objects.

## Run With Docker

From repository root:

```bash
docker compose up --build
```

Run in background:

```bash
docker compose up -d --build
```

Check services:

```bash
docker compose ps
```

Stop and remove containers:

```bash
docker compose down
```

Useful endpoints after startup:

- Gateway API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- RabbitMQ UI: `http://localhost:15672`
- pgAdmin: `http://localhost:5050`

## Option 1: Local Editable Install

In another project, from this repository root:

```bash
pip install -e ./packages/commonpackages
```

Then import:

```python
from commonpackages.models import DataRecord, Base
from commonpackages.sensor import TemperatureSensor, VibrationSensor
```

## Option 2: Build and Install Wheel

```bash
cd packages/commonpackages
python -m build
pip install dist/commonpackages-1.0.0-py3-none-any.whl
```

## Minimal Integration Pattern

1. Reuse `DataRecord` in your SQLAlchemy metadata setup.
2. Accept device payload in your API service.
3. Publish payload to a queue (or process directly if queue is not needed).
4. Persist using `DataRecord` shape (`value`, `data_type`, `extra_data`, `timestamp`).

## Compatibility Notes

- Python requirement: `>=3.8`
- Core dependency in package: `sqlalchemy>=2.0.0`
