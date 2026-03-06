# iCloud CLI

A command-line interface for interacting with iCloud services including Calendar and iCloud Drive.

## 🚀 Quick Start

### **Recommended: Use Virtual Environment**

```bash
# 1. Create and activate virtual environment
python3 -m venv icli_env
source icli_env/bin/activate  # Linux/Mac
# icli_env\Scripts\activate   # Windows

# 2. Clone the repository
git clone https://github.com/wassx/icli.git
cd icli

# 3. Install dependencies (for real iCloud data)
pip install pyicloud keyring requests

# 4. Run the CLI
python main.py

# 5. When done
deactivate
```

### **Alternative: System-wide Installation**

```bash
# Clone the repository
git clone https://github.com/wassx/icli.git
cd icli

# Install dependencies (for real iCloud data)
pip install --user pyicloud keyring requests

# Run the CLI
python main.py
```

### **For Development**

```bash
# Run tests
python test_security.py
python test_ux_improvements.py
python test_oauth.py
python test_real_data_simple.py
python test_drive_browser.py

# Run demos
python quickstart.py
python demo.py
```

**⚠️ Important**: This CLI now **requires authentication** for all features. Install dependencies and log in to access your real iCloud data.

**💡 Tip**: Using a virtual environment (`python3 -m venv`) is recommended to avoid conflicts with system Python packages.

## 📋 Features

### Calendar Module 🚧 (Real Data Ready)
- **List upcoming events**: From actual iCloud calendar (with authentication)
- **Mock data fallback**: Sample events when not authenticated
- Create new events (planned)
- Edit/delete existing events (planned)
- Calendar selection support (planned)

### iCloud Drive Module ✅ (Interactive File Browser)
- **Interactive file tree browser**: Navigate directories with numbered selection
- **Real-time directory listing**: Load files from actual iCloud Drive (with authentication)
- **Intelligent file display**: Directories first, then files with emoji icons (📁/📄)
- **Human-readable sizes**: Automatic formatting (KB, MB, GB, TB)
- **Breadcrumb navigation**: Clear path display and parent directory access
- **File details view**: Metadata, size, dates, and download options
- **File caching**: Performance optimization for repeated navigation
- **Interactive commands**: Navigate, refresh, download, quit
- **Mock data fallback**: Sample structure when not authenticated

## 📂 Project Structure

```
icli/
├── icli/                  # Main package
│   ├── __init__.py        # Package initialization
│   ├── calendar.py        # Calendar functionality
│   └── drive.py           # iCloud Drive functionality
├── main.py                # Main CLI entry point
├── demo.py                # Demo script
├── test_menu.py           # Menu tests
├── test_drive_browser.py  # Drive browser tests
├── README.md              # This file
├── agent.md               # Development guidelines
├── requirements.txt       # Dependencies
└── setup.py               # Package configuration
```

## 🔐 Authentication & UX

The CLI now supports real iCloud data access through Apple ID authentication with a focus on user experience and safety.

### Authentication Features
- **Secure login**: Apple ID + password with optional keyring storage
- **Two-factor authentication**: Full 2FA support with clear guidance
- **Session management**: Persistent sessions with trusted device support
- **Graceful fallback**: Automatic switch to mock data if authentication fails
- **Immediate redirection**: Automatic auth prompt when accessing services
- **Contextual menus**: Different options based on authentication status

### UX Improvements
- **Welcome screen**: Clear welcome message with current mode indication
- **Guided authentication**: Step-by-step login process with validation
- **Helpful information**: Contextual help and security reassurance
- **Clear feedback**: Visual indicators for authentication status
- **Recovery options**: Easy ways to continue if login fails
- **Demo mode**: Full functionality with mock data

### Security Enhancements
- **Password security**: Hidden input using getpass module
- **Read-only mode**: No write operations possible
- **Secure credential handling**: Optional keyring integration
- **Input validation**: Email format and password length checks
- **2FA guidance**: Clear instructions for verification codes
- **Privacy information**: Transparent data access policies
- **Session monitoring**: Trusted device status indicators
- **Professional interface**: Reduced emojis, clear messaging
- **Error handling**: Graceful fallback and recovery options

### User Flow

#### First Time Users
1. **Welcome screen** shows current mode (Demo)
2. **Select any service** (Mail, Calendar, Drive)
3. **Authentication prompt** appears automatically
4. **Choose option**: Login, Demo mode, or Exit
5. **If login**: Enter credentials and complete 2FA
6. **If demo mode**: Continue with mock data

#### Returning Users
1. **Welcome screen** shows authentication status
2. **Direct access** to services if already logged in
3. **Seamless experience** with saved credentials (optional)
4. **Easy logout** from authentication menu

#### Authentication Process
1. Run `python main.py`
2. Select "Authentication" from main menu OR
3. Select any service to trigger auto-auth prompt
4. Choose "Login to iCloud"
5. Enter Apple ID (validated for email format)
6. Enter password (validated for minimum length)
7. Complete 2FA with clear instructions
8. Access real iCloud data automatically

### Authentication Menu Options

**When Not Logged In:**
- 🔓 **Login to iCloud**: Full authentication process
- ❓ **About authentication**: Security and process information
- ⬅️ **Back to main menu**: Return to main menu

**When Logged In:**
- 🔒 **Logout**: Securely end session
- 📋 **Account info**: Session details and data access
- ⬅️ **Back to main menu**: Return to main menu

### Security Notes
- Passwords are securely stored using system keyring (optional)
- No write operations are performed (read-only mode)
- All sensitive data is handled securely

## 🎯 Usage

### Main Menu
```
=== iCloud CLI ===
1) Calendar
2) iCloud Drive
3) Authentication
4) Exit
```

### iCloud Drive Browser
```
=== iCloud Drive Browser ===
📁 Navigating your iCloud Drive files
Commands: [number] to enter, b=back, q=quit, r=refresh

📁 iCloud Drive / Documents / Work

📁 Contents (8 items):
------------------------------------------------------------
 1. 📁 Projects/ 1.2 MB
 2. 📁 Archives/ 456.7 KB
 3. 📄 report.pdf 2.3 MB
 4. 📄 presentation.pptx 8.1 MB
 5. 📄 data.csv 1.5 KB

📂 Enter choice:
```

**Navigation Commands:**
- **Numbers (1-99)**: Enter directory or view file details
- **b**: Go back to parent directory
- **r**: Refresh file list (clear cache)
- **q**: Quit browser

**File Detail Options:**
- **d**: Download this file
- **b**: Back to directory listing

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
- **Autonomous atomic commit policy**
- Code quality standards
- API integration patterns
- Testing strategy
- **Documentation-first approach**

## 📦 Dependencies

### Required for Real iCloud Data
```
pyicloud>=1.0.1    # iCloud API access
keyring>=24.2.0    # Secure credential storage
requests>=2.31.0   # HTTP requests
```

### Installation Methods

#### Virtual Environment (Recommended)
```bash
python3 -m venv icli_env
source icli_env/bin/activate
pip install -r requirements.txt
```

#### User Installation
```bash
pip install --user -r requirements.txt
```

#### System Installation
```bash
sudo pip install -r requirements.txt
```

### Troubleshooting Installation Issues

#### "Externally Managed Environment" Error
If you see this error:
```
error: externally-managed-environment
```

**Solutions:**

1. **Use virtual environment (recommended)**:
```bash
python3 -m venv icli_env
source icli_env/bin/activate
pip install pyicloud keyring requests
```

2. **Use --user flag**:
```bash
pip install --user pyicloud keyring requests
```

3. **Use system package manager**:
```bash
sudo apt install python3-pip python3-venv  # Debian/Ubuntu
sudo pip install pyicloud keyring requests
```

4. **Override protection (not recommended)**:
```bash
pip install --break-system-packages pyicloud keyring requests
```

#### Permission Errors
```bash
pip install --user pyicloud keyring requests
```

#### SSL Errors
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pyicloud keyring requests
```

## 🚀 Roadmap

### Phase 1: Core Functionality ✅
- [x] Basic CLI structure with menu system
- [x] Calendar module with mock data
- [x] iCloud Drive interactive file browser
- [x] File navigation and detail views
- [x] Human-readable file sizes and caching

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
**Current Version**: 0.2.0
**Last Updated**: November 2024