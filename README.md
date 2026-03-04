# iCloud CLI

A command-line interface for interacting with iCloud services including Mail, Calendar, and iCloud Drive.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/wassx/icli.git
cd icli

# Install dependencies (for real iCloud data)
pip install pyicloud keyring requests

# Quick demo (non-interactive, uses mock data)
python quickstart.py

# Interactive CLI with real data support
python main.py

# Test real data integration
python test_real_data_simple.py

# Read-only functionality demo
python demo_readonly.py
```

**Note**: For real iCloud data, install dependencies first. The CLI will automatically fall back to mock data if authentication fails or dependencies are missing.

## 📋 Features

### Mail Module ✅ (Read-Only with Real Data Support)
- **Unread Email Overview**: Quick summary of unread emails with sender, subject, date, and preview
- **Email Detail View**: Full email content with proper formatting
- **Real Data Integration**: Loads emails from actual iCloud account (with authentication)
- **Mock Data Fallback**: Uses sample data when not authenticated or for testing
- **Email Management**: Mark as read only (reply, forward, delete disabled)
- **Send Email**: Disabled in read-only mode
- **Security Focus**: No write operations to protect email integrity

### Calendar Module 🚧 (Real Data Ready)
- **List upcoming events**: From actual iCloud calendar (with authentication)
- **Mock data fallback**: Sample events when not authenticated
- Create new events (planned)
- Edit/delete existing events (planned)
- Calendar selection support (planned)

### iCloud Drive Module 🚧 (Real Data Ready)
- **File listing**: From actual iCloud Drive (with authentication)
- **Mock data fallback**: Sample file structure when not authenticated
- Upload/download files (planned)
- File metadata display (planned)
- Folder navigation (planned)

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

## 🔐 Authentication

The CLI now supports real iCloud data access through Apple ID authentication.

### Authentication Features
- **Secure login**: Apple ID + password with optional keyring storage
- **Two-factor authentication**: Full 2FA support
- **Session management**: Persistent sessions with trusted device support
- **Graceful fallback**: Automatic switch to mock data if authentication fails

### How to Authenticate
1. Run `python main.py`
2. Select "Authentication" from the main menu
3. Choose "Login"
4. Enter your Apple ID and password
5. Complete 2FA if required
6. Access real iCloud data from all modules

### Security Notes
- Passwords are securely stored using system keyring (optional)
- No write operations are performed (read-only mode)
- All sensitive data is handled securely

## 🎯 Usage

### Main Menu
```
=== iCloud CLI ===
1) Mail
2) Calendar
3) iCloud Drive
4) Authentication  ← New!
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