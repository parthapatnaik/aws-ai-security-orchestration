import json
from decimal import Decimal


def convert_numbers(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: convert_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [convert_numbers(v) for v in value]
    return value


def log_event(stage, **fields):
    payload = {"stage": stage, **fields}
    print(json.dumps(payload, default=str))
