# iCloud CLI

A command-line interface for interacting with iCloud services including Mail, Calendar, and iCloud Drive.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/wassx/icli.git
cd icli

# Install dependencies
pip install -r requirements.txt

# Quick demo (non-interactive)
python quickstart.py

# Interactive CLI (requires user input)
python main.py

# Read-only functionality demo
python demo_readonly.py
```

**Note**: `python main.py` requires interactive input. Use `python quickstart.py` for a non-interactive demonstration of all features.

## 📋 Features

### Mail Module ✅ (Read-Only)
- **Unread Email Overview**: Quick summary of unread emails with sender, subject, date, and preview
- **Email Detail View**: Full email content with proper formatting
- **Email Management**: Mark as read only (reply, forward, delete disabled)
- **Send Email**: Disabled in read-only mode
- **Security Focus**: No write operations to protect email integrity

### Calendar Module 🚧
- List upcoming events
- Create new events
- Edit/delete existing events
- Calendar selection support

### iCloud Drive Module 🚧
- File listing with pagination
- Upload/download files
- File metadata display
- Folder navigation

## 📂 Project Structure

```
icli/
├── icli/                  # Main package
│   ├── __init__.py        # Package initialization
│   ├── mail.py            # Mail functionality
│   ├── calendar.py        # Calendar functionality
│   └── drive.py           # iCloud Drive functionality
├── main.py                # Main CLI entry point
├── demo.py                # Demo script
├── demo_mail.py           # Mail demo
├── test_menu.py           # Menu tests
├── test_mail.py           # Mail tests
├── README.md              # This file
├── MAIL_FEATURES.md       # Mail feature documentation
├── agent.md               # Development guidelines
├── requirements.txt       # Dependencies
└── setup.py               # Package configuration
```

## 🎯 Usage

### Main Menu
```
=== iCloud CLI ===
1) Mail
2) Calendar
3) iCloud Drive
4) Other
5) Exit
```

### Mail Functionality (Read-Only)
1. **List unread emails**: Shows overview of all unread emails
2. **Read email**: Select an email number to view full content
3. **Manage email**: Mark as read only (no write operations)
4. **Send email**: ❌ Disabled in read-only mode

**Note**: This CLI operates in read-only mode for security. No emails can be sent, replied to, forwarded, or deleted.

## 🔧 Development

### Setup
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests
```bash
python test_menu.py
python test_mail.py
```

### Development Guidelines
See `agent.md` for detailed development instructions including:
- Atomic commit requirements
- Code quality standards
- API integration patterns
- Testing strategy

## 📦 Dependencies

Current dependencies are minimal for development:
```
# requirements.txt
# Add any required packages here
# pyicloud for actual iCloud integration
```

## 🚀 Roadmap

### Phase 1: Core Functionality ✅
- [x] Basic CLI structure with menu system
- [x] Mail module with mock data
- [x] Email listing and detail views
- [x] Email management options
- [x] Send email functionality

### Phase 2: API Integration 🚧
- [ ] iCloud authentication (Apple ID + 2FA)
- [ ] Real API connections using pyicloud
- [ ] Error handling and retry logic
- [ ] Rate limiting management

### Phase 3: Advanced Features 🚀
- [ ] Search functionality across services
- [ ] Notifications and alerts
- [ ] Batch operations
- [ ] Configuration management
- [ ] Caching for offline use

### Phase 4: Polish 🎨
- [ ] Comprehensive testing suite
- [ ] Performance optimization
- [ ] User documentation
- [ ] Package distribution (PyPI)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following the guidelines in `agent.md`
4. Commit with atomic commits: `git commit -m "Add feature"`
5. Push to your branch: `git push origin feature/your-feature`
6. Create a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📬 Contact

For questions or support, please open an issue on GitHub.

---

**Project Status**: Active Development
**Current Version**: 0.1.0
**Last Updated**: March 2026