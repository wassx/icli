# Authentication Guide

iCLI authenticates with iCloud using your **Apple ID** and an **app-specific password**.  
Credentials are stored in the **system keyring** — never in plain-text files.

---

## First-time setup

### 1 — Generate an app-specific password

Apple requires app-specific passwords for third-party tools that access iCloud.

1. Go to [appleid.apple.com](https://appleid.apple.com)
2. Sign in → **Sign-In & Security** → **App-Specific Passwords**
3. Click **+** and give it a label (e.g. `iCLI`)
4. Copy the generated password (`xxxx-xxxx-xxxx-xxxx`)

> Your regular Apple ID password will not work here.

### 2 — Run interactive login

```bash
python main.py auth login
```

You will be prompted for:
- **Apple ID** — your iCloud e-mail address
- **Password** — the app-specific password from step 1
- **6-digit 2FA code** — (if required) sent to your trusted iPhone / iPad / Mac

After successful login the credentials are saved to the system keyring.  
**All subsequent commands resume the session silently — no prompts needed.**

---

## Session behaviour

| Situation | What happens |
|-----------|-------------|
| Valid keyring entry found | Session resumes silently at startup |
| Session expired (>24 h) | In-memory state cleared; re-login prompted in the interactive menu or raised as `RuntimeError` in scripting mode |
| Wrong password entered | Saved keyring entry deleted so stale credentials cannot loop |
| Logout | Session cleared and keyring entry removed |

Sessions last **24 hours** by default. The interactive menu offers `Authentication → Extend session timer` to renew for another 24 hours without re-entering credentials.

---

## Two-factor authentication

If your Apple ID has 2FA enabled (required for most accounts):

1. `auth login` detects `requires_2fa` from the pyicloud service object.
2. A code is sent to all trusted devices.
3. You enter the 6-digit code at the prompt.
4. The session is established and saved.

**2FA is only needed for the initial interactive login.**  
Once the session is saved in the keyring, automated/non-interactive use works without 2FA until the session expires or is invalidated by Apple.

If your account requires 2FA and you only have access to a headless server, set up the session once on a machine with a terminal, then copy the keyring entry to the server using your OS keyring migration tools.

---

## Environment variables (CI / automation)

For pipelines and containers where a keyring is not available or you want to inject credentials externally:

```bash
export ICLOUD_APPLE_ID="you@icloud.com"
export ICLOUD_PASSWORD="xxxx-xxxx-xxxx-xxxx"

python main.py calendar events --json
```

Or per-command:

```bash
ICLOUD_APPLE_ID=you@icloud.com ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx \
  python main.py drive list --json
```

> **Security note:** Environment variables are visible to other processes on the same machine. Prefer the keyring for interactive use;  use environment variables only in isolated CI environments.

---

## Check authentication status

```bash
# Human-readable
python main.py auth status

# JSON (for scripts)
python main.py auth status --json
```

Example output:

```json
{
  "authenticated": true,
  "apple_id": "you@icloud.com",
  "access": "read-only",
  "session_expires_in_seconds": 79200
}
```

---

## Logout

```bash
python main.py auth logout
```

This:
1. Clears the in-memory session object.
2. **Removes the saved entry from the system keyring.**

After logout every tool invocation will raise an error in scripting mode until `auth login` is run again.

---

## Keyring backend

iCLI uses Python's [`keyring`](https://pypi.org/project/keyring/) library which selects the appropriate backend automatically:

| Platform | Backend |
|----------|---------|
| macOS | macOS Keychain |
| Linux + GNOME / KDE | Secret Service (libsecret / kwallet) |
| Windows | Windows Credential Manager |
| Headless Linux | `keyrings.alt` file backend (installed as a fallback) |

If no suitable backend is detected, iCLI will warn that credentials cannot be saved and will prompt for credentials on every run.

---

## Troubleshooting

**"Not authenticated and no credentials available"**  
→ Run `python main.py auth login` interactively first.

**"Authentication failed. Check your credentials."**  
→ Verify your Apple ID and app-specific password. Regular Apple ID passwords are not accepted by third-party apps.

**"Two-factor authentication required" in scripting mode**  
→ The saved session has expired or been revoked. Run `python main.py auth login` again to refresh it.

**Session expires very quickly**  
→ Apple may be flagging unusual access. Try using the Extend session option (`Authentication → Extend session timer`) instead of re-logging in.
