import json

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate


def get_response_from_entities(list_of_objs):
    return [obj.to_dict() for obj in list_of_objs]


def datetime_to_str(timestamp):
    if not timestamp or timestamp == 'None':
        return ""
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def get_valid_value(dict_name, key):
    val = dict_name.get(key)
    val = {} if val is None else val
    return val


def validate_schema(filepath, schema_key, input_json):
    try:
        f = open(filepath)
        data = json.load(f)
        f.close()
        schema = data.get(schema_key, None)

        if schema is None:
            raise "schema not found"

        validate(instance=input_json, schema=schema)

    except ValidationError as e:
        response = e.message
        print("failed validation")
    except Exception as e:
        print("failed")
