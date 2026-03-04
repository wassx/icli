# iCloud CLI - Complete Solution Guide

## **Issue: Seeing Mock Data When "Logged In"**

This guide explains why you're seeing mock data and how to fix it.

## **Root Cause**

The CLI is designed to **gracefully fall back to mock data** when:
1. Required dependencies are missing
2. Authentication fails
3. API connection issues occur

## **Current Status Check**

Run the debug script to see your current status:
```bash
python debug_auth.py
```

## **Solution: Install Missing Dependencies**

### **1. Install Required Packages**

```bash
pip install pyicloud keyring requests
```

### **2. Verify Installation**

```bash
python3 -c "import pyicloud, keyring; print('✅ All dependencies installed')"
```

### **3. Run the CLI**

```bash
python main.py
```

## **What Changes After Installation**

### **Before (Current Issue)**
```
❌ Shows "Logged in" but uses mock data
❌ No real iCloud connection
❌ Missing pyicloud/keyring dependencies
```

### **After (Fixed)**
```
✅ Real Apple ID authentication
✅ Actual iCloud emails/events/files
✅ Session management with auto-refresh
✅ OAuth token support
```

## **Detailed Troubleshooting**

### **1. Dependency Issues**

**Symptom**: "Logged in" but seeing mock data

**Solution**: Install missing packages:
```bash
pip install pyicloud keyring requests
```

### **2. Authentication Problems**

**Symptom**: Login fails or 2FA issues

**Solutions**:
- Ensure correct Apple ID and password
- Complete 2FA if enabled on your account
- Check internet connection
- Verify Apple ID account status

### **3. API Connection Issues**

**Symptom**: Connection errors or timeouts

**Solutions**:
- Check internet connectivity
- Verify Apple services status
- Try again later if Apple servers are down

## **How the System Works**

### **Dependency Detection**
```python
# In auth.py __init__ method
self._check_dependencies()  # Warns about missing packages
```

### **Graceful Fallback**
```python
# In mail.py _load_real_emails method
if not self.auth.is_authenticated():
    print("Not authenticated. Using mock data.")
    self._load_mock_emails()  # Fallback to mock data
```

### **Authentication Flow**
```
1. User selects service → Authentication check
2. If not authenticated → Show login prompt
3. If dependencies missing → Show installation instructions
4. If login successful → Load real data
5. If login fails → Continue with mock data
```

## **Installation Guide**

### **Method 1: pip (Recommended)**

```bash
pip install pyicloud keyring requests
```

### **Method 2: requirements.txt**

```bash
pip install -r requirements.txt
```

### **Method 3: Manual Installation**

```bash
pip install pyicloud
pip install keyring
pip install requests
```

## **Verification Steps**

### **1. Check Installed Packages**

```bash
pip list | grep -E "(pyicloud|keyring|requests)"
```

### **2. Test Import**

```bash
python3 -c "import pyicloud, keyring, requests; print('All dependencies OK')"
```

### **3. Run Debug Script**

```bash
python debug_auth.py
```

Should show:
```
✅ pyicloud is available
✅ keyring is available
```

### **4. Test Real Authentication**

```bash
python main.py
```

Then:
1. Select any service (Mail, Calendar, Drive)
2. Choose "Login to iCloud"
3. Enter your Apple ID and password
4. Complete 2FA if required
5. Access your real iCloud data!

## **Common Issues & Solutions**

### **Issue: "ModuleNotFoundError: No module named 'pyicloud'"**

**Solution**: Install pyicloud:
```bash
pip install pyicloud
```

### **Issue: "ModuleNotFoundError: No module named 'keyring'"**

**Solution**: Install keyring:
```bash
pip install keyring
```

### **Issue: "pip command not found"**

**Solution**: Use pip3 or install pip:
```bash
python3 -m pip install pyicloud keyring requests
```

### **Issue: "Permission denied" when installing**

**Solution**: Use --user flag or sudo:
```bash
pip install --user pyicloud keyring requests
# or
sudo pip install pyicloud keyring requests
```

## **Alternative: Continue with Demo Mode**

If you can't install dependencies, the CLI works perfectly in demo mode:

```bash
python main.py
```

Features available in demo mode:
- ✅ Full menu system
- ✅ Mock email data (Amazon, GitHub, Netflix examples)
- ✅ Read-only functionality
- ✅ All UX improvements
- ✅ Session simulation

## **Technical Details**

### **Dependency Requirements**

| Package | Version | Purpose |
|---------|---------|---------|
| pyicloud | 1.0.1+ | iCloud API access |
| keyring | 24.2.0+ | Secure credential storage |
| requests | 2.31.0+ | HTTP requests |

### **Mock Data vs Real Data**

**Mock Data** (Demo Mode):
- Predefined sample emails
- No authentication required
- Works without dependencies
- Great for testing

**Real Data** (After Installation):
- Your actual iCloud emails
- Requires Apple ID login
- Needs pyicloud dependency
- Full functionality

## **Support & Resources**

### **Documentation**
- `README.md` - Main documentation
- `MAIL_FEATURES.md` - Mail module details
- `agent.md` - Development guidelines

### **Tests**
- `test_security.py` - Security features
- `test_ux_improvements.py` - UX features
- `test_oauth.py` - OAuth/session management
- `test_real_data_simple.py` - Real data integration

### **Demos**
- `quickstart.py` - Non-interactive demo
- `demo_readonly.py` - Read-only demo
- `debug_auth.py` - Debug authentication

## **Final Notes**

The iCloud CLI is designed to work in **both modes**:

1. **Demo Mode** - No installation required, uses mock data
2. **Real Mode** - Install dependencies, access real iCloud data

**Choose the mode that works for you!**

- **For quick testing**: Use demo mode
- **For real iCloud access**: Install dependencies
- **For development**: Both modes available

The system gracefully handles missing dependencies by falling back to demo mode, ensuring you always have a working experience.

## **Need Help?**

If you're still having issues after following this guide:

1. Run `python debug_auth.py` and share the output
2. Check `pip list` for installed packages
3. Verify your Python environment
4. Contact support with the above information

Happy iCloud CLI-ing! 🎉