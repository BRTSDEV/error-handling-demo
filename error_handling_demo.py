import json
import logging
import time
from functools import wraps
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

class ConfigError(Exception):
    """Base class for all config-related errors."""


class ConfigNotFoundError(ConfigError):
    """The config file does not exist."""


class ConfigInvalidError(ConfigError):
    """The config file exists but its content is wrong."""


def load_config(path):
    """Load a JSON config file and return it as a dict.

    Raises ConfigNotFoundError, ConfigInvalidError or ConfigError.
    """
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as err:
        # "from err" keeps the original error in the traceback for debugging.
        raise ConfigNotFoundError(f"Config file not found: {path}") from err
    except PermissionError as err:
        raise ConfigError(f"No permission to read: {path}") from err
    except json.JSONDecodeError as err:
        raise ConfigInvalidError(
            f"Invalid JSON in {path} (line {err.lineno}, column {err.colno})"
        ) from err
    else:
        # Runs only if the try block had NO error.
        log.info("Loaded config from %s", path)
    finally:
        # Runs always, error or not. Good for cleanup and logging.
        log.debug("Finished trying to read %s", path)

    if not isinstance(data, dict):
        raise ConfigInvalidError(f"Config must be a JSON object, got {type(data).__name__}")
    return data

def parse_port(value):
    """Turn a value into a valid TCP port number (1-65535)."""
    try:
        port = int(value)
    except (TypeError, ValueError) as err:
        raise ConfigInvalidError(f"Port must be a number, got {value!r}") from err
    if not 1 <= port <= 65535:
        raise ConfigInvalidError(f"Port must be between 1 and 65535, got {port}")
    return port

def retry(times=3, delay=0.2, exceptions=(ConnectionError,)):
    """Retry a function when it raises one of `exceptions`."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as err:
                    if attempt == times:
                        log.error("Giving up after %d attempts: %s", times, err)
                        raise
                    log.warning("Attempt %d/%d failed (%s), retrying...", attempt, times, err)
                    time.sleep(delay)

        return wrapper

    return decorator


_calls = {"count": 0}


@retry(times=3, delay=0.1)
def flaky_service():
    """Pretend network call: fails twice, then works."""
    _calls["count"] += 1
    if _calls["count"] < 3:
        raise ConnectionError("server not reachable")
    return "connected"

def main():
    # Make a small valid config file to play with.
    Path("demo_config.json").write_text('{"host": "localhost", "port": "8080"}', encoding="utf-8")

    print("\n1) Valid config")
    config = load_config("demo_config.json")
    print("   port ->", parse_port(config["port"]))

    print("\n2) Missing file")
    try:
        load_config("does_not_exist.json")
    except ConfigNotFoundError as err:
        print("   handled:", err)

    print("\n3) Broken JSON")
    Path("broken.json").write_text('{"host": "localhost",', encoding="utf-8")
    try:
        load_config("broken.json")
    except ConfigError as err:  # catches any config error via the base class
        print("   handled:", err)

    print("\n4) Bad port")
    for bad in ("abc", 70000, None):
        try:
            parse_port(bad)
        except ConfigInvalidError as err:
            print("   handled:", err)

    print("\n5) Retry decorator")
    print("   result ->", flaky_service())

    # Clean up the demo files.
    Path("demo_config.json").unlink(missing_ok=True)
    Path("broken.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
