import json


def _load_secrets(location: str, require_data: bool = False) -> dict:
    try:
        with open(location) as file:
            data = json.load(file)
            if require_data and not data:
                raise ValueError(f"Vault secrets have no data at {location}")

            return data
    except FileNotFoundError as exc:
        raise Exception(f"Error loading secrets at {location}. File not found.") from exc


def get_database_secrets(require_data: bool = False) -> dict:
    return _load_secrets("/vault/secrets/database", require_data)


def get_redis_secrets(require_data: bool = False) -> dict:
    return _load_secrets("/vault/secrets/redis", require_data)
