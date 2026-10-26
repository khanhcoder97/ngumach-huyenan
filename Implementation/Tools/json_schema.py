"""Minimal JSON Schema subset used by the content and contract validators."""

import json
import math
import re


def validate(instance, schema, label, errors):
    expected_type = schema.get("type")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{label}: expected constant {schema['const']!r}")
        return False
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{label}: value {instance!r} not in enum")
        return False

    if expected_type == "object":
        if not isinstance(instance, dict):
            errors.append(f"{label}: expected object")
            return False
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{label}: missing required property '{key}'")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                validate(value, properties[key], f"{label}.{key}", errors)
            elif additional is False:
                errors.append(f"{label}: unexpected property '{key}'")
    elif expected_type == "array":
        if not isinstance(instance, list):
            errors.append(f"{label}: expected array")
            return False
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{label}: array has fewer than minItems")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{label}: array items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                validate(item, item_schema, f"{label}[{index}]", errors)
    elif expected_type == "string":
        if not isinstance(instance, str):
            errors.append(f"{label}: expected string")
            return False
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{label}: string is shorter than minLength")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, instance) is None:
            errors.append(f"{label}: string does not match pattern {pattern}")
    elif expected_type == "integer":
        if isinstance(instance, bool) or not isinstance(instance, int):
            errors.append(f"{label}: expected integer")
            return False
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{label}: value below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{label}: value above maximum")
    elif expected_type == "number":
        if isinstance(instance, bool) or not isinstance(instance, (int, float)):
            errors.append(f"{label}: expected number")
            return False
        if not math.isfinite(instance):
            errors.append(f"{label}: number is not finite")
            return False
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{label}: value below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{label}: value above maximum")
    elif expected_type == "boolean":
        if not isinstance(instance, bool):
            errors.append(f"{label}: expected boolean")
            return False
    return True
