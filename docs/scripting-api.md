# Scripting & Agent API

`icli.api.ICloudAPI` is a clean Python interface designed for use in automation scripts, AI agents, and pipelines.

**Key properties:**
- All methods return plain `dict` / `list` objects — safe to pass directly to `json.dumps()`.
- Errors raise `RuntimeError` (auth/service failures) or `ValueError` (bad arguments), never print diagnostics.
- No `input()` calls — fully non-interactive.
- Thread-safe for read access (does not mutate shared state during data calls).

---

## Installation / import

```python
from icli.api import ICloudAPI
```

No additional install step is required beyond the project dependencies (`pyicloud`, `keyring`, `requests`).

---

## Minimal example

```python
from icli.api import ICloudAPI

api = ICloudAPI()
api.authenticate()                              # resumes saved keyring session

for cal in api.list_calendars():
    print(cal["name"], cal["id"])

events = api.list_events(calendar_name="Work", days=7)
for e in events:
    print(e["start"], e["title"])
```

---

## Authentication

### `ICloudAPI.authenticate(apple_id=None, password=None) → dict`

Establish a session. Credential resolution order:

1. `apple_id` / `password` keyword arguments
2. `ICLOUD_APPLE_ID` / `ICLOUD_PASSWORD` environment variables
3. Saved keyring entry (silent resume — **preferred path for agents**)

**Returns** the same dict as `auth_status()`.

**Raises `RuntimeError`** when no credentials are available *and* no saved session exists, or when login fails. Interactive 2FA cannot be completed non-interactively — run `python main.py auth login` once to store credentials.

```python
import os
os.environ["ICLOUD_APPLE_ID"] = "you@icloud.com"
os.environ["ICLOUD_PASSWORD"] = "xxxx-xxxx-xxxx-xxxx"  # app-specific password

api = ICloudAPI()
api.authenticate()
```

---

### `ICloudAPI.auth_status() → dict`

Returns the current session state without attempting to authenticate.

```python
status = api.auth_status()
# {
#   "authenticated": True,
#   "apple_id": "you@icloud.com",
#   "access": "read-only",
#   "session_expires_in_seconds": 82340
# }
```

| Key | Type | Description |
|-----|------|-------------|
| `authenticated` | bool | Active session present |
| `apple_id` | str \| None | Authenticated Apple ID |
| `access` | str \| None | `"read-only"` when authenticated, else `None` |
| `session_expires_in_seconds` | int | Seconds until expiry (only when authenticated) |

---

### `ICloudAPI.logout() → dict`

Clear the session and remove saved keyring credentials.

```python
result = api.logout()
# {"ok": True, "message": "Logged out"}
```

---

## Calendar

### `ICloudAPI.list_calendars() → list[dict]`

Return all iCloud calendars.

```python
calendars = api.list_calendars()
# [
#   {"id": 1, "name": "Work",     "color": "#0E60CF", "default": False},
#   {"id": 2, "name": "Personal", "color": "#1CB84A", "default": True },
# ]
```

| Key | Type | Description |
|-----|------|-------------|
| `id` | int | 1-based index |
| `name` | str | Display name |
| `color` | str | Hex colour string |
| `default` | bool | Default calendar flag |

---

### `ICloudAPI.list_events(calendar_name=None, days=14) → list[dict]`

Return upcoming events, sorted by start date.

```python
# All calendars, next 14 days (default)
events = api.list_events()

# Work calendar, next 7 days
events = api.list_events(calendar_name="Work", days=7)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `calendar_name` | str \| None | None | Partial, case-insensitive calendar name filter |
| `days` | int | 14 | Look-ahead window |

**Raises `ValueError`** when `calendar_name` is given but no matching calendar is found.

**Event dict fields:**

| Key | Type | Description |
|-----|------|-------------|
| `title` | str | Event title (`"Untitled"` if blank) |
| `start` | ISO 8601 str \| None | Start date/time |
| `end` | ISO 8601 str \| None | End date/time |
| `all_day` | bool | All-day event flag |
| `recurring` | bool | Recurring event flag |
| `location` | str \| None | Location string |
| `calendar` | str \| None | Parent calendar name |

```python
import json
print(json.dumps(events, indent=2))
# [
#   {
#     "title": "Standup",
#     "start": "2026-03-09T09:00:00",
#     "end":   "2026-03-09T09:30:00",
#     "all_day": false,
#     "recurring": true,
#     "location": null,
#     "calendar": "Work"
#   },
#   ...
# ]
```

---

## iCloud Drive

### `ICloudAPI.list_files(path="/") → list[dict]`

List the contents of an iCloud Drive directory.

```python
root   = api.list_files()
docs   = api.list_files(path="/Documents")
nested = api.list_files(path="/Documents/Projects")
```

**Raises `ValueError`** when the path does not exist.

**Item dict fields:**

| Key | Type | Description |
|-----|------|-------------|
| `name` | str | File or folder name |
| `type` | `"file"` \| `"folder"` | Item type |
| `path` | str | Full iCloud Drive path |
| `size_bytes` | int | Size in bytes (0 for folders) |
| `size` | str | Human-readable, e.g. `"4.2 MB"` |

```python
import json
print(json.dumps(api.list_files("/Documents"), indent=2))
```

---

### `ICloudAPI.search_files(query="", file_type=None, min_size=None, max_size=None) → list[dict]`

Recursively search all of iCloud Drive for files matching every provided filter.  
All filters are optional — omit them to match all files.

```python
# All PDF files ≥ 500 KB
pdfs = api.search_files(file_type="pdf", min_size=500 * 1024)

# Files with "report" in the name
reports = api.search_files(query="report")

# Files between 1 MB and 10 MB
medium = api.search_files(min_size=1_048_576, max_size=10_485_760)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | str | Text to match anywhere in the filename (case-insensitive) |
| `file_type` | str \| None | Extension filter, e.g. `"pdf"`, `"docx"` |
| `min_size` | int \| None | Minimum file size in **bytes** |
| `max_size` | int \| None | Maximum file size in **bytes** |

**Result dict fields** — same as `list_files()`, plus:

| Key | Type | Description |
|-----|------|-------------|
| `extension` | str | Lowercase file extension (no dot) |
| `formatted_size` | str | Human-readable size |

---

### `ICloudAPI.download_file(remote_path, local_path=None) → dict`

Download a file from iCloud Drive to the local filesystem.

```python
# Download to current directory (keeps original filename)
result = api.download_file("/Documents/report.pdf")
# {"ok": True, "local_path": "/home/user/report.pdf", "size_bytes": 614400, "size": "600.0 KB"}

# Download to a specific path
result = api.download_file("/Documents/report.pdf", local_path="~/Downloads/report.pdf")

# Download into a directory (keeps original filename)
result = api.download_file("/Documents/report.pdf", local_path="/tmp/")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `remote_path` | str | Absolute iCloud Drive path, e.g. `"/Documents/report.pdf"` |
| `local_path` | str \| None | Local file or directory destination (default: file's name in cwd) |

**Result dict:**

| Key | Type | Description |
|-----|------|-------------|
| `ok` | bool | `True` on success, `False` on failure |
| `local_path` | str | Absolute local path of the saved file |
| `size_bytes` | int | Downloaded file size in bytes |
| `size` | str | Human-readable size |
| `error` | str | Present only when `ok` is `False` |

---

## Error handling pattern

```python
from icli.api import ICloudAPI

api = ICloudAPI()

try:
    api.authenticate()
except RuntimeError as e:
    # Not authenticated and no keyring entry — need interactive login first
    print(f"Auth required: {e}")
    raise SystemExit(1)

try:
    events = api.list_events(calendar_name="NoSuchCalendar")
except ValueError as e:
    print(f"Bad argument: {e}")

try:
    files = api.list_files("/DoesNotExist")
except ValueError as e:
    print(f"Path error: {e}")
```

---

## Agent integration example

```python
import json
from icli.api import ICloudAPI

def get_todays_events():
    api = ICloudAPI()
    api.authenticate()              # silent resume from keyring
    return api.list_events(days=1)  # today only

if __name__ == "__main__":
    events = get_todays_events()
    print(json.dumps(events, indent=2))
```

Or via the shell (for agents that call subprocesses):

```bash
python main.py calendar events --days 1 --json
```
