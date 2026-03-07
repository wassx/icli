# iCLI

```
 _  ___ _    ___ 
(_)/ __| |  |_ _|
| | (__| |__ | | 
|_|\___|____|___|
```

Command-line interface and Python API for **iCloud Calendar** and **iCloud Drive**.

> Read-only. iCLI never modifies or deletes any iCloud data.

---

## Install

```bash
git clone <repo>
cd icli
python -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
```

---

## First login

Run once interactively to save credentials to the system keyring.  
Apple requires an **app-specific password** — generate one at  
[appleid.apple.com → Sign-In & Security → App-Specific Passwords](https://appleid.apple.com).

```bash
python main.py auth login
```

```
📧 Apple ID:
   Enter your Apple ID email: you@icloud.com

Password:
   Enter your password:

🔄 Connecting to iCloud...
🔐 Two-Factor Authentication Required
   Enter 6-digit verification code: 123456
   ✅ Two-factor authentication successful

Authentication Successful!
   Session will expire in 24 hours
```

Every subsequent call resumes the saved session silently — no prompts.

---

## Interactive menu

```bash
python main.py
```

```
 _  ___ _    ___ 
(_)/ __| |  |_ _|
| | (__| |__ | | 
|_|\___|____|___|
════════════════════════════════════════════════
✅ Session resumed for you@icloud.com

=== iCloud CLI - 🔒 Logged in ===
1) Calendar
2) iCloud Drive
3) Authentication
4) Exit

Enter your choice (1-4):
```

---

## Non-interactive CLI

All commands work without the interactive menu.  
Append `--json` to get machine-readable output.

### Auth

```bash
# Check session state
python main.py auth status

# authenticated: False

python main.py auth status --json
# {
#   "authenticated": true,
#   "apple_id": "you@icloud.com",
#   "access": "read-only",
#   "session_expires_in_seconds": 82340
# }

# Save credentials interactively
python main.py auth login

# Remove session and keyring entry
python main.py auth logout --json
# {"ok": true, "message": "Logged out"}
```

### Calendar

```bash
# List all calendars
python main.py calendar list --json
# [
#   {"id": 1, "name": "Work",     "color": "#0E60CF", "default": false},
#   {"id": 2, "name": "Personal", "color": "#1CB84A", "default": true}
# ]

# Upcoming events — next 14 days (default)
python main.py calendar events --json

# Events in a specific calendar, narrower window
python main.py calendar events --calendar Work --days 7 --json
# [
#   {
#     "title": "Standup",
#     "start": "2026-03-09T09:00:00",
#     "end":   "2026-03-09T09:30:00",
#     "all_day": false,
#     "recurring": true,
#     "location": null,
#     "calendar": "Work"
#   }
# ]
```

### iCloud Drive

```bash
# List root directory
python main.py drive list --json
# [
#   {"name": "Documents", "type": "folder", "path": "/Documents", "size_bytes": 0,       "size": "0 B"   },
#   {"name": "photo.jpg", "type": "file",   "path": "/photo.jpg", "size_bytes": 3145728, "size": "3.0 MB"}
# ]

# List a subdirectory
python main.py drive list --path /Documents --json

# Search by filename
python main.py drive search report --json

# Search with filters
python main.py drive search --type pdf --min 500 --json
# [
#   {
#     "name": "Q1 report.pdf",
#     "path": "/Documents/Q1 report.pdf",
#     "size_bytes": 614400,
#     "size": "600.0 KB",
#     "type": "file",
#     "extension": "pdf",
#     "formatted_size": "600.0 KB"
#   }
# ]

# Files between 1 MB and 10 MB
python main.py drive search --min 1024 --max 10240 --json
```

---

## Python API

For scripts and AI agents that need to call iCLI programmatically.

```python
from icli.api import ICloudAPI

api = ICloudAPI()
api.authenticate()          # resumes keyring session silently

# Calendar
calendars = api.list_calendars()
# [{"id": 1, "name": "Work", "color": "#0E60CF", "default": False}, ...]

events = api.list_events(calendar_name="Work", days=7)
# [{"title": "Standup", "start": "2026-03-09T09:00:00", ...}, ...]

# Drive
files = api.list_files(path="/Documents")
# [{"name": "report.pdf", "type": "file", "size": "600.0 KB", ...}, ...]

results = api.search_files(query="report", file_type="pdf", min_size=500*1024)
# [{"name": "Q1 report.pdf", "path": "/Documents/Q1 report.pdf", ...}, ...]
```

All methods return plain `dict`/`list` objects safe for `json.dumps()`.  
They raise `RuntimeError` (auth / service failure) or `ValueError` (bad argument)  
and never call `input()` or print to stdout.

### Credential injection (CI / agents)

```python
import os
os.environ["ICLOUD_APPLE_ID"] = "you@icloud.com"
os.environ["ICLOUD_PASSWORD"] = "xxxx-xxxx-xxxx-xxxx"

api = ICloudAPI()
api.authenticate()
```

Or from the shell:

```bash
ICLOUD_APPLE_ID=you@icloud.com \
ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx \
python main.py calendar events --json
```

---

## Pipe-friendly output

```bash
# Print today's event titles with jq
python main.py calendar events --days 1 --json | jq '.[].title'

# Count files in a directory
python main.py drive list --path /Documents --json | jq length

# Find large PDFs and extract paths
python main.py drive search --type pdf --min 10240 --json \
  | jq -r '.[].path'
```

---

## Command reference

```
python main.py [--apple-id EMAIL] [--password PASSWORD] COMMAND SUBCOMMAND [--json]

auth
  status              Current session state
  login               Interactive login; saves to keyring
  logout              Clear session and keyring

calendar
  list                List all calendars
  events              Upcoming events
    --calendar NAME   Filter by calendar (partial match)
    --days N          Look-ahead window (default: 14)

drive
  list                Directory listing
    --path PATH       Target path (default: /)
  search              Recursive file search
    [query]           Filename text filter
    --type EXT        Extension filter (pdf, docx, …)
    --min NKB         Minimum size in KB
    --max NKB         Maximum size in KB
```

Full reference: [docs/cli-reference.md](docs/cli-reference.md)  
Python API: [docs/scripting-api.md](docs/scripting-api.md)  
Authentication: [docs/authentication.md](docs/authentication.md)

---

## Project layout

```
icli/
  api.py        ICloudAPI — scripting/agent interface
  auth.py       Session management, 2FA, keyring
  calendar.py   Calendar module
  drive.py      Drive module
  utils.py      Spinner, separator
main.py         Interactive menu + argparse dispatcher
docs/           CLI reference, API docs, auth guide
tests/          Test suite
examples/       demo.py, quickstart.py
```

---

## Limitations

- **Read-only** — no uploads, edits, or deletions
- **Unofficial API** — Apple's iCloud endpoints are undocumented and may change
- **2FA** — first login requires an interactive terminal; subsequent runs are silent

---

## Disclaimer

See [DISCLAIMER.md](DISCLAIMER.md). Use at your own risk.
