# Error Handling Demo

A small Python project by **BRTSDEV** that shows practical error handling patterns in one readable file.

## What it demonstrates

- **Custom exceptions** with a base class (`ConfigError`) and specific subclasses
- **Specific `except` blocks** instead of a catch-all `except Exception`
- **`try / except / else / finally`** and when each part runs
- **Exception chaining** with `raise ... from err` so the original cause is kept
- **Input validation** (`parse_port`) instead of trusting data
- **A reusable `@retry` decorator** for flaky operations
- **Logging** instead of `print` for warnings and errors
- **Tests with pytest** that check the errors actually happen

## Run it

```bash
python error_handling_demo.py
```

## Test it

```bash
pip install pytest
pytest
```

## What I learned

- Catch the most specific exception you can, and let unexpected ones crash loudly.
- Custom exceptions make calling code much easier to write.
- `from err` makes debugging far easier because the real cause is not lost.
- Testing the failure cases matters as much as testing the happy path.

## Ideas to extend it

- Load settings from environment variables as a fallback
- Add exponential backoff to the retry decorator
- Write errors to a log file
