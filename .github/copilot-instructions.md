# Copilot Instructions for iCloud CLI

## Project Overview

**icli** is a Python command-line interface for interacting with Apple iCloud services (Mail, Calendar, iCloud Drive). The project uses the `pyicloud` library for real iCloud data access and falls back to mock data when unauthenticated.

- **Language**: Python 3.6+
- **Entry point**: `main.py`
- **Package**: `icli/` (contains `auth.py`, `mail.py`, `calendar.py`, `drive.py`)
- **Tests**: `test_*.py` files in the project root

## Architecture

The project follows a modular architecture where each iCloud service lives in its own module under `icli/`:

- `icli/auth.py` — Apple ID authentication, 2FA handling, session management
- `icli/mail.py` — Mail listing and display (read-only)
- `icli/calendar.py` — Calendar event listing
- `icli/drive.py` — iCloud Drive file listing
- `main.py` — CLI menu loop and user interaction

Each service module provides a real-data path (via `pyicloud`) and a mock-data fallback for use when unauthenticated or in tests.

## Coding Standards

- **Indentation**: 4 spaces (PEP 8)
- **Type hints**: Use Python type hints on all public methods and function signatures
- **Docstrings**: All public classes and methods must have docstrings
- **Error handling**: Use try/except with specific exception types; always fall back gracefully (see `agent.md` for the recommended pattern)
- **Read-only**: No write operations are performed against iCloud; the CLI is intentionally read-only for safety

## API Integration Pattern

When adding new iCloud service features, follow the three-method pattern:

```python
def real_api_method(self):
    """Real implementation using iCloud API"""
    try:
        result = self._api_client.make_call()
        return self._process_result(result)
    except ApiError as e:
        self._handle_api_error(e)
        return None

def mock_api_method(self):
    """Mock implementation for development/testing"""
    return self._mock_data

def api_method(self):
    """Public method — uses real or mock based on authentication state"""
    if self._use_real_api:
        return self.real_api_method()
    return self.mock_api_method()
```

## Testing

- Test files are named `test_*.py` and run directly with `python test_<name>.py`
- Tests must not require real iCloud credentials; use mock data / `unittest.mock`
- Cover normal paths, empty/edge cases, and error conditions
- See `test_mail.py` and `test_security.py` for examples of the expected style

Run tests:
```bash
python test_security.py
python test_ux_improvements.py
python test_oauth.py
python test_menu.py
python test_mail.py
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt        # or: pip install pyicloud keyring requests

# Run the CLI
python main.py
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `pyicloud` | iCloud API access |
| `keyring` | Secure credential storage |
| `requests` | HTTP requests |

## Key Conventions

- **Authentication**: Always check `cli.auth.is_authenticated()` before accessing real data; never hard-code credentials
- **Menu flow**: Use numbered menus with clear back-navigation; prompt `input()` only at the end of a menu block
- **Output**: Prefer plain-text output with minimal emoji; use emoji only where already established (e.g., `✅`, `❌`)
- **Commit style**: Imperative mood, ≤72 chars on the first line (see `agent.md`)
- **README**: Update `README.md` whenever user-visible behaviour, features, or dependencies change
