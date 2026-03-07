# iCLI — iCloud Command-Line Interface

```
 _  ___ _    ___ 
(_)/ __| |  |_ _|
| | (__| |__ | | 
|_|\___|____|___|
```

A terminal interface and scripting API for **iCloud Calendar** and **iCloud Drive**.
Works in two modes: an interactive menu for humans and a non-interactive CLI + Python API for scripts and agents.

> ⚠️ **Read-only.** iCLI never writes to or deletes any iCloud data.  
> See [DISCLAIMER.md](DISCLAIMER.md) for full terms.

---

## Features

| Area | What you can do |
|------|----------------|
| **Calendar** | List calendars, browse events, monthly grid view |
| **iCloud Drive** | Browse the file tree, list a path, search by name / type / size |
| **Authentication** | Secure keyring storage, 2FA, auto-resume saved sessions |
| **Scripting** | Full argparse CLI with `--json` output; importable `ICloudAPI` class |

---

## Requirements

- Python 3.8+
- `pyicloud` — iCloud API client
- `keyring` — secure credential storage
- `requests` — HTTP

```bash
pip install pyicloud keyring requests
```

Or with the virtual environment from the repo:

```bash
python -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
```

---

## Quick Start

### 1 — First-time login (interactive, stores credentials in system keyring)

```bash
python main.py auth login
```

Enter your Apple ID e-mail and password when prompted. If two-factor authentication is required, a 6-digit code will be sent to your trusted devices.

### 2 — Interactive menu

```bash
python main.py
```

```
 _  ___ _    ___ 
(_)/ __| |  |_ _|
| | (__| |__ | | 
|_|\___|____|___|
════════════════════════════════════════
✅ Session resumed for you@icloud.com

=== iCloud CLI - 🔒 Logged in ===
1) Calendar
2) iCloud Drive
3) Authentication
4) Exit
```

### 3 — Non-interactive / scripting mode

```bash
# Authentication status
python main.py auth status --json

# List calendars as JSON
python main.py calendar list --json

# Upcoming events for the next 7 days
python main.py calendar events --days 7 --json

# List iCloud Drive root
python main.py drive list --json

# Search for PDF files larger than 500 KB
python main.py drive search --type pdf --min 500 --json
```

---

## CLI Reference

Full command reference: **[docs/cli-reference.md](docs/cli-reference.md)**

```
python main.py [--apple-id EMAIL] [--password PASSWORD] COMMAND SUBCOMMAND [options] [--json]

Commands:
  auth      status | login | logout
  calendar  list | events [--calendar NAME] [--days N]
  drive     list [--path PATH] | search [query] [--type EXT] [--min NKB] [--max NKB]
```

---

## Python Scripting API

For agents and automation scripts that need to call iCLI programmatically:

```python
from icli.api import ICloudAPI

api = ICloudAPI()
api.authenticate()                              # silent keyring resume

calendars = api.list_calendars()
events    = api.list_events(calendar_name="Work", days=7)
files     = api.list_files(path="/Documents")
results   = api.search_files(query="report", file_type="pdf")
```

All methods return plain `dict`/`list` objects safe to pass to `json.dumps()`.  
They raise `RuntimeError` or `ValueError` on error and never call `input()` or print to stdout.

Full reference: **[docs/scripting-api.md](docs/scripting-api.md)**

---

## Authentication

iCLI stores credentials in the **system keyring** (macOS Keychain, GNOME Keyring, Windows Credential Manager).

```bash
python main.py auth login      # interactive; saves to keyring
python main.py auth status     # show session state
python main.py auth logout     # clear session and keyring entry
```

For CI/automation, supply credentials via environment variables:

```bash
export ICLOUD_APPLE_ID="you@icloud.com"
export ICLOUD_PASSWORD="your-app-specific-password"
python main.py calendar events --json
```

Full guide: **[docs/authentication.md](docs/authentication.md)**

---

## Project Layout

```
icli/
  __init__.py      iCloudCLI entry-point class
  api.py           Non-interactive ICloudAPI (scripting)
  auth.py          Session management, 2FA, keyring
  calendar.py      Calendar module
  drive.py         Drive module
  utils.py         Shared UI helpers (Spinner, separator)
main.py            Interactive menu + argparse CLI dispatcher
tests/             Unit and integration tests
examples/          demo.py, quickstart.py
docs/              CLI reference, API reference, auth guide
```

---

## Limitations

- **Read-only** — no writes, uploads, or deletions
- **Unofficial API** — Apple's iCloud API is undocumented; it may change
- **2FA** — first login requires an interactive terminal; subsequent runs resume silently

---

## License

MIT — see [LICENSE](LICENSE) file.  
Third-party libraries (`pyicloud`, `keyring`, `requests`) carry their own licences.