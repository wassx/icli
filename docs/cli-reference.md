# CLI Reference

iCLI exposes every feature through a non-interactive command-line interface.  
When called **without arguments** it opens the interactive menu.  
When called **with arguments** it runs a single command and exits.

---

## Global options

```
python main.py [--apple-id EMAIL] [--password PASSWORD] COMMAND ...
```

| Option | Description |
|--------|-------------|
| `--apple-id EMAIL` | Apple ID e-mail. Overrides the `ICLOUD_APPLE_ID` env var and the keyring entry. |
| `--password PASSWORD` | Password. Overrides `ICLOUD_PASSWORD`. Prefer the keyring; avoid plain-text passwords in shell history. |

---

## `auth` — Authentication

### `auth status [--json]`

Print the current session state and exit.

```bash
python main.py auth status
python main.py auth status --json
```

**Output fields**

| Field | Type | Description |
|-------|------|-------------|
| `authenticated` | bool | Whether a valid session is active |
| `apple_id` | str \| null | The authenticated Apple ID |
| `access` | str \| null | `"read-only"` when authenticated |
| `session_expires_in_seconds` | int | Seconds left before the session expires (omitted when not authenticated) |

**Example JSON**
```json
{
  "authenticated": true,
  "apple_id": "you@icloud.com",
  "access": "read-only",
  "session_expires_in_seconds": 82340
}
```

---

### `auth login [--json]`

Interactive login; saves credentials to the system keyring.  
Run this **once** before using any scripting commands.

```bash
python main.py auth login
```

You will be prompted for your Apple ID, password, and (if required) a 6-digit two-factor authentication code sent to your trusted devices.  
After a successful login all subsequent commands resume the session silently.

---

### `auth logout [--json]`

Clear the active session and **remove saved credentials** from the keyring.

```bash
python main.py auth logout
python main.py auth logout --json
```

---

## `calendar` — Calendar

All calendar commands require an authenticated session.

### `calendar list [--json]`

List all calendars visible in iCloud.

```bash
python main.py calendar list
python main.py calendar list --json
```

**Output fields per item**

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | 1-based index |
| `name` | str | Calendar display name |
| `color` | str | Calendar colour (as reported by iCloud) |
| `default` | bool | Whether this is the default calendar |

**Example JSON**
```json
[
  { "id": 1, "name": "Work",     "color": "#0E60CF", "default": false },
  { "id": 2, "name": "Personal", "color": "#1CB84A", "default": true  }
]
```

---

### `calendar events [options] [--json]`

List upcoming events, optionally filtered by calendar and date window.

```bash
python main.py calendar events
python main.py calendar events --days 7
python main.py calendar events --calendar Work --days 14 --json
```

| Option | Default | Description |
|--------|---------|-------------|
| `--calendar NAME` | all | Partial, case-insensitive calendar name filter |
| `--days N` | 14 | Look-ahead window in days |

**Output fields per event**

| Field | Type | Description |
|-------|------|-------------|
| `title` | str | Event title |
| `start` | ISO 8601 str | Start date/time |
| `end` | ISO 8601 str | End date/time |
| `all_day` | bool | True for all-day events |
| `recurring` | bool | True for recurring events |
| `location` | str \| null | Location string |
| `calendar` | str \| null | Name of the parent calendar |

**Example JSON**
```json
[
  {
    "title": "Standup",
    "start": "2026-03-09T09:00:00",
    "end":   "2026-03-09T09:30:00",
    "all_day": false,
    "recurring": true,
    "location": null,
    "calendar": "Work"
  }
]
```

---

## `drive` — iCloud Drive

All drive commands require an authenticated session.

### `drive list [--path PATH] [--json]`

List the contents of an iCloud Drive directory.

```bash
python main.py drive list
python main.py drive list --path /Documents
python main.py drive list --path "/Work Projects" --json
```

| Option | Default | Description |
|--------|---------|-------------|
| `--path PATH` | `/` | Absolute iCloud Drive path |

**Output fields per item**

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | File or folder name |
| `type` | `"file"` \| `"folder"` | Item type |
| `path` | str | Full iCloud Drive path |
| `size_bytes` | int | Size in bytes (0 for folders) |
| `size` | str | Human-readable size, e.g. `"4.2 MB"` |

**Example JSON**
```json
[
  { "name": "Documents", "type": "folder", "path": "/Documents", "size_bytes": 0,       "size": "0 B"     },
  { "name": "photo.jpg", "type": "file",   "path": "/photo.jpg", "size_bytes": 3145728, "size": "3.0 MB"  }
]
```

---

### `drive search [query] [options] [--json]`

Recursively search iCloud Drive for files matching all provided filters.

```bash
python main.py drive search report
python main.py drive search budget --type xlsx
python main.py drive search --type pdf --min 500 --json
python main.py drive search --min 1024 --max 10240 --json
```

| Argument / Option | Description |
|-------------------|-------------|
| `query` | Text to match anywhere in the filename (case-insensitive, omit to match all) |
| `--type EXT` | File extension filter, e.g. `pdf`, `docx`, `jpg` |
| `--min NKB` | Minimum file size in **kilobytes** |
| `--max NKB` | Maximum file size in **kilobytes** |

**Output fields per result** — same schema as `drive list`, plus:

| Field | Type | Description |
|-------|------|-------------|
| `extension` | str | File extension (lowercase, no dot) |

---

## `--json` flag

Append `--json` to any leaf command to get machine-readable output on `stdout`.

- Progress messages and spinners are suppressed.
- Errors are written to `stderr` as `{"ok": false, "error": "…"}`.
- Exit code is `0` on success, `1` on error.

```bash
# Pipe to jq
python main.py calendar events --json | jq '.[].title'

# Check exit code
python main.py auth status --json && echo "OK"
```

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `ICLOUD_APPLE_ID` | Apple ID e-mail (used when `--apple-id` is absent) |
| `ICLOUD_PASSWORD` | App-specific password (used when `--password` is absent) |

Apple requires an **app-specific password** when using third-party tools.  
Generate one at [appleid.apple.com](https://appleid.apple.com) → Sign-In & Security → App-Specific Passwords.
