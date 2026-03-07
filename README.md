# iCloud CLI

A command-line interface for iCloud services.

## ⚠️ DISCLAIMER

**USE AT YOUR OWN RISK** - No liability for data loss or issues.

## Features

### Current Functionality
- **Calendar**: View calendars and events (read-only)
- **iCloud Drive**: Browse files, search by name/type/size

### Usage
```bash
python main.py
```

### Requirements
- Python 3.8+
- `pyicloud` library for real iCloud access

## Quick Start

1. Install dependencies: `pip install pyicloud keyring requests`
2. Run: `python main.py`
3. Log in with Apple ID when prompted

## Limitations

- **Read-only mode only** - No file modifications
- **Experimental** - Apple may change APIs
- **No official support** - Use with caution

## License

MIT - See LICENSE file for details.