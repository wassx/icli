# iCLI

```
 _  ___ _    ___ 
(_)/ __| |  |_ _|
| | (__| |__ | | 
|_|\___|____|___|
```

Command-line interface and Python API for **iCloud Calendar**, **iCloud Drive**, and **iCloud Mail**.

> Read-only. iCLI never modifies or deletes any iCloud data.

---

## Install

### Pre-built binary (recommended)

Download the latest binary for your platform from
[Releases](../../releases/latest):

| Platform | File |
|----------|------|
| Linux x86_64 | `icli-linux-amd64` |
| macOS (Apple Silicon & Intel via Rosetta) | `icli-macos-arm64` |
| Windows x86_64 | `icli-windows-amd64.exe` |

**Linux / macOS:**

```bash
# Download (example: Linux)
curl -Lo icli https://github.com/<owner>/icli/releases/latest/download/icli-linux-amd64
chmod +x icli
sudo mv icli /usr/local/bin/

# Verify
icli --help
```

Or install without `sudo`:

```bash
chmod +x icli-linux-amd64
mkdir -p ~/.local/bin
mv icli-linux-amd64 ~/.local/bin/icli
# Make sure ~/.local/bin is in your PATH (add to ~/.bashrc if needed):
# export PATH="$HOME/.local/bin:$PATH"
icli --help
```

**Windows (PowerShell):**

```powershell
Invoke-WebRequest -Uri https://github.com/<owner>/icli/releases/latest/download/icli-windows-amd64.exe -OutFile icli.exe
.\icli.exe --help
```

No Python, pip, or virtual environment required.

### From source

```bash
git clone <repo>
cd icli
python -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
```

When running from source, replace `icli` with `python main.py` in all
examples below.

---

## First login

Run once interactively to save credentials to the system keyring.  
Apple requires an **app-specific password** — generate one at  
[appleid.apple.com → Sign-In & Security → App-Specific Passwords](https://appleid.apple.com).

```bash
icli auth login
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

### Mail password

iCloud Mail uses IMAP and may need its own app-specific password.
The first time you open **iCloud Mail** in interactive mode, you'll be prompted to enter one.
It's verified on the spot and saved to the system keyring.

You can also set it via environment variable:

```bash
export ICLOUD_MAIL_PASSWORD="xxxx-xxxx-xxxx-xxxx"
```

---

## Quick examples

```bash
# Check session
icli auth status --json

# List calendars
icli calendar list --json

# Next 7 days of events in "Work" calendar
icli calendar events --calendar Work --days 7 --json

# Browse iCloud Drive
icli drive list --json
icli drive list --path /Documents --json

# Search for PDFs over 500 KB
icli drive search --type pdf --min 500 --json

# Download a file
icli drive download /Documents/report.pdf
icli drive download /Documents/report.pdf -o ~/Downloads/report.pdf --json

# List mail folders
icli mail folders --json

# Latest 20 inbox emails
icli mail list --json

# Read a specific email by UID
icli mail read 12345 --json
```

All commands support `--json` for machine-readable output.

---

## Interactive menu

```bash
icli
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

### Browsing & downloading in the interactive Drive browser

Select **2) iCloud Drive** to open the file browser. Navigate with numbers,
then press **d** on any file to download it:

```
📁 Contents (3 items):
─────────────────────────────
 0. 📁 .. (Parent Directory)
 1. 📁 Documents/ 1.2 MB
 2. 📄 photo.jpg 3.0 MB
 3. 📄 report.pdf 600.0 KB

📂 Enter choice (number, 0=up, r=refresh, b/q=quit): 3

📄 File Details: report.pdf
─────────────────────────────
Type:  File
Path:  /report.pdf
Size:  600.0 KB (614,400 bytes)

Options:
d. Download this file
b. Back to directory listing

Choose option (d/b): d
Enter local filename for report.pdf (or 'q' to cancel):
📥 Downloading report.pdf to report.pdf...
✅ Download completed: report.pdf
```

---

## Non-interactive CLI

All commands work without the interactive menu.  
Append `--json` to get machine-readable output.

### Auth

```bash
icli auth status
# authenticated: False

icli auth status --json
# {
#   "authenticated": true,
#   "apple_id": "you@icloud.com",
#   "access": "read-only",
#   "session_expires_in_seconds": 82340
# }

# Save credentials interactively
icli auth login

# Remove session and keyring entry
icli auth logout --json
# {"ok": true, "message": "Logged out"}
```

### Calendar

```bash
# List all calendars
icli calendar list --json
# [
#   {"id": 1, "name": "Work",     "color": "#0E60CF", "default": false},
#   {"id": 2, "name": "Personal", "color": "#1CB84A", "default": true}
# ]

# Upcoming events — next 14 days (default)
icli calendar events --json

# Events in a specific calendar, narrower window
icli calendar events --calendar Work --days 7 --json
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
icli drive list --json
# [
#   {"name": "Documents", "type": "folder", "path": "/Documents", "size_bytes": 0,       "size": "0 B"   },
#   {"name": "photo.jpg", "type": "file",   "path": "/photo.jpg", "size_bytes": 3145728, "size": "3.0 MB"}
# ]

# List a subdirectory
icli drive list --path /Documents --json

# Search by filename
icli drive search report --json

# Search with filters
icli drive search --type pdf --min 500 --json
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
icli drive search --min 1024 --max 10240 --json

# Download a file
icli drive download /Documents/report.pdf
icli drive download /Documents/report.pdf --output ~/Downloads/report.pdf --json
# {"ok": true, "local_path": "/home/user/Downloads/report.pdf", "size_bytes": 614400, "size": "600.0 KB"}
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

# Download
result = api.download_file("/Documents/report.pdf")
result = api.download_file("/Documents/report.pdf", local_path="~/Downloads/")
# {"ok": True, "local_path": "/home/user/Downloads/report.pdf", ...}

# Mail
folders = api.list_mail_folders()
emails = api.list_emails(folder="INBOX", limit=10)
full = api.get_email(uid="12345")
# {"subject": "Meeting", "body_text": "Hi, ...", "attachments": [...], ...}
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
icli calendar events --json
```

---

## Pipe-friendly output

```bash
# Print today's event titles with jq
icli calendar events --days 1 --json | jq '.[].title'

# Count files in a directory
icli drive list --path /Documents --json | jq length

# Find large PDFs and extract paths
icli drive search --type pdf --min 10240 --json \
  | jq -r '.[].path'

# Download all PDFs in a folder
icli drive search --type pdf --json \
  | jq -r '.[].path' \
  | while read -r p; do icli drive download "$p" -o ./pdfs/; done

# List unread email subjects
icli mail list --json | jq '[.[] | select(.seen == false)] | .[].subject'

# Get email body as plain text
icli mail read 12345 --json | jq -r '.body_text'
```

---

## Command reference

```
icli [--apple-id EMAIL] [--password PASSWORD] COMMAND SUBCOMMAND [--json]

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
  download PATH       Download a file locally
    -o, --output FILE Local destination (default: cwd)

mail
  folders             List mail folders
  list                List recent emails
    --folder FOLDER   Mail folder (default: INBOX)
    --limit N         Number of emails (default: 20)
  read UID            Read a specific email
    --folder FOLDER   Mail folder (default: INBOX)
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
  mail.py       Mail module (IMAP)
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
