# iCloud CLI Development Agent Instructions

## CRITICAL RULES (MUST READ FIRST)

### 📝 Documentation First - No Exceptions
**MUST keep README.md up-to-date with EVERY change**
- Every feature addition, removal, or modification requires immediate README update
- Documentation must be updated in the same commit as the code change
- Test all README examples before considering work complete
- Outdated documentation is a critical failure

### 🔄 Atomic Commit Policy
- **MUST make atomic commits autonomously** for completed, tested work
- **One logical change per commit** - small, focused, independent changes
- **Include README updates** in the same commit as feature changes
- **Follow standard format** with descriptive messages
- **Never combine unrelated changes** in a single commit

## Project Overview

This document provides instructions for the AI agent working on the iCloud CLI project. It outlines the development approach, coding standards, and specific guidelines for implementing features.

## Development Principles

### 1. Modular Architecture
- **Maintain Separation**: Keep each iCloud service (Mail, Calendar, Drive) in separate modules
- **Single Responsibility**: Each function should do one thing well
- **Loose Coupling**: Modules should be independent and interchangeable

### 2. User Experience
- **CLI-First**: Design for terminal usage with clear prompts and feedback
- **Progressive Disclosure**: Show simple options first, details on demand
- **Error Handling**: Graceful degradation with helpful error messages

### 3. Code Quality
- **Readability**: Clear variable names, consistent indentation (4 spaces)
- **Documentation**: Docstrings for all public methods and classes
- **Type Hints**: Use Python type hints for better code clarity
- **Testing**: Include unit tests for all major functionality

### 4. Documentation First
- **MUST keep README.md up-to-date**: Update README for every significant change
- **Document before implementing**: Add feature documentation first
- **Update usage examples**: Keep examples current with actual functionality
- **Maintain feature status**: Update ✅/🚧 indicators in README

## Implementation Guidelines

### Adding New Features

1. **Plan First**: Create a simple design document before coding
2. **Mock Data**: Start with mock data, then connect to real API
3. **Incremental**: Build features step by step with verification at each stage
4. **Test**: Write tests before or alongside implementation

### API Integration Pattern

```python
# Recommended pattern for API integration

def real_api_method(self):
    """Real implementation using iCloud API"""
    try:
        # Actual API call
        result = self._api_client.make_call()
        return self._process_result(result)
    except ApiError as e:
        self._handle_api_error(e)
        return None

def mock_api_method(self):
    """Mock implementation for development/testing"""
    # Return mock data
    return self._mock_data

def api_method(self):
    """Public method - uses real or mock based on configuration"""
    if self._use_real_api:
        return self.real_api_method()
    else:
        return self.mock_api_method()
```

### Error Handling

```python
# Recommended error handling approach

def safe_api_call(self):
    """Wrapper for safe API calls"""
    try:
        result = self._make_api_call()
        return result
    except AuthenticationError:
        print("Error: Please authenticate first")
        return None
    except NetworkError:
        print("Error: Network connection failed")
        return None
    except ApiError as e:
        print(f"API Error: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        # Log error for debugging
        return None
```

## Specific Feature Instructions

### Mail Module Enhancements

**Priority Features:**
1. **Real API Integration**: Use pyicloud library
2. **Authentication**: Apple ID OAuth flow
3. **Email Folders**: Support Inbox, Sent, Drafts, etc.
4. **Search**: Implement email search functionality

**Implementation Steps:**
```python
# Example: Adding real email fetching

def _fetch_emails_from_api(self):
    """Fetch emails from iCloud API"""
    from pyicloud import PyiCloudService
    
    api = PyiCloudService(self._apple_id, self._password)
    if not api.requires_2fa:
        mail_service = api.mail
        return mail_service.emails()
    else:
        # Handle 2FA
        raise AuthenticationError("2FA required")
```

### Calendar Module Development

**Required Features:**
- List upcoming events
- Create new events
- Edit/delete existing events
- Calendar selection (work, personal, etc.)

**Data Structure:**
```python
class CalendarEvent:
    def __init__(self, title, start_datetime, end_datetime, 
                 location=None, description=None, calendar_name="Default"):
        self.title = title
        self.start = start_datetime
        self.end = end_datetime
        self.location = location
        self.description = description
        self.calendar = calendar_name
```

### iCloud Drive Module

**Core Functionality:**
- File listing with pagination
- Upload/download with progress
- File metadata (size, type, date)
- Folder navigation

**File Operations:**
```python
# Recommended upload pattern
def upload_file(self, local_path, remote_path):
    """Upload file with progress tracking"""
    file_size = os.path.getsize(local_path)
    
    with open(local_path, 'rb') as f:
        # Use API to upload with progress callback
        result = self._api.upload_file(f, remote_path, 
                                      progress_callback=self._show_progress)
    
    return result
```

## Testing Strategy

### Unit Tests
- Test each module independently
- Use mock data and patch API calls
- Test edge cases and error conditions

### Integration Tests
- Test module interactions
- Verify data flow between components
- Test complete user workflows

### Example Test Structure
```python
def test_mail_listing():
    """Test email listing functionality"""
    mail = MailModule()
    
    # Test with mock data
    emails = mail.list_emails()
    assert len(emails) > 0
    assert all('subject' in email for email in emails)
    
    # Test empty case
    mail._unread_emails = []
    result = mail.list_emails()
    assert result == "No unread emails."
```

## Documentation Standards

### Code Documentation
- **Module-level**: Purpose, main classes/functions
- **Class-level**: Responsibility, key methods
- **Method-level**: Purpose, parameters, return value, exceptions

### User Documentation
- **README.md**: Overview, installation, basic usage
- **Feature-specific MD files**: Detailed usage examples
- **Inline help**: Add `--help` support to CLI

## Version Control

### Commit Messages
- Use imperative mood: "Add feature" not "Added feature"
- First line: 50-72 characters summarizing change
- Body: Explanation of what and why (not how)
- Reference issues: "Fixes #123" or "Related to #456"

### Atomic Commits (Autonomous)
- **MUST make atomic commits autonomously**: Commit completed, tested work without user prompt
- **One logical change per commit**: Each commit represents a single feature, fix, or improvement
- **Small and focused**: Keep commits minimal and independent
- **Complete and tested**: Only commit work that is fully implemented and verified
- **Standard format required**: Use imperative mood with co-author attribution

**Autonomous Commit Process:**
1. Complete a logical unit of work
2. Test thoroughly
3. Update README.md if applicable
4. Make atomic commit with standard format
5. Continue with next logical unit

**Required Commit Format:**
```bash
# Autonomous atomic commit example
git commit -m "Add iCloud Drive file browser navigation"

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>
```

**When to Commit:**
- ✅ Feature implementation complete and tested
- ✅ Bug fix verified and working
- ✅ Documentation updates (including README)
- ✅ Refactoring that maintains functionality

**When NOT to Commit:**
- ❌ Partial or broken implementations
- ❌ Untested code
- ❌ Multiple unrelated changes
- ❌ Without README updates (if applicable)

### Commit Examples

**Good - Atomic commit:**
```bash
git commit -m "Add email detail view functionality"

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>
```

**Bad - Multiple changes:**
```bash
# Avoid: Combining unrelated changes
git commit -m "Add email features and fix calendar bug"
```

**Good - Separate commits:**
```bash
# First commit
git commit -m "Add email detail view functionality"

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>

# Second commit
git commit -m "Fix calendar event parsing error"

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>
```

### Branch Strategy
- `main`: Stable, production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature development
- `bugfix/*`: Hotfixes and bug corrections

## Deployment

### Package Structure
```
setup.py          # Package configuration
requirements.txt  # Dependencies
MANIFEST.in       # Additional files to include
pyproject.toml    # Modern build configuration
```

### Distribution
```bash
# Build and publish
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

## Troubleshooting Guide

### Common Issues

**API Connection Problems:**
- Check internet connection
- Verify credentials
- Handle 2FA requirements
- Check API rate limits

**Dependency Conflicts:**
- Use virtual environments
- Pin specific versions in requirements.txt
- Test with clean environments

**Input/Output Errors:**
- Validate all user input
- Handle file permissions
- Check disk space for large operations

## Future Roadmap

### Phase 1: Core Functionality (Current)
- [x] Basic CLI structure
- [x] Mail module with mock data
- [ ] Calendar module skeleton
- [ ] Drive module skeleton

### Phase 2: API Integration
- [ ] iCloud authentication
- [ ] Real API connections
- [ ] Error handling and retry logic

### Phase 3: Advanced Features
- [ ] Search functionality
- [ ] Notifications
- [ ] Batch operations
- [ ] Configuration management

### Phase 4: Polish
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] User documentation
- [ ] Package distribution

## Agent Workflow

1. **Understand Request**: Clarify requirements if needed
2. **Plan**: Outline approach before coding
3. **Implement**: Write clean, documented code
4. **Test**: Verify functionality works
5. **Document**: Update relevant documentation
6. **Update README**: **MUST always update README.md** with new features, changes, or improvements
7. **Review**: Check for improvements

### README Update Requirements

**CRITICAL: MUST keep README.md up-to-date with every change**
- **No exceptions**: Every feature addition, removal, or modification requires README update
- **Update first**: Add documentation before or alongside implementation
- **Verify accuracy**: Test all examples and commands in README
- **Feature status**: Maintain accurate ✅/🚧 indicators

**README must always contain current information about:**
- Project description and purpose
- Installation instructions (tested and working)
- Usage examples (verified to work)
- Complete feature list with current status
- Accurate roadmap and progress
- Up-to-date dependency information
- Current contribution guidelines

**README update workflow:**
```bash
# 1. Implement feature
# 2. Write/Update tests
# 3. Update README with new documentation
# 4. Verify all README examples work
# 5. Commit everything together
git add src/feature.py
git add test_feature.py
git add README.md  # MUST include README
git commit -m "Add feature X with complete documentation"
```

**Consequences of outdated README:**
- User confusion and frustration
- Broken examples and instructions
- Loss of trust in documentation
- Increased support burden
- Poor onboarding experience

## Decision Making

**When to Ask for Clarification:**
- Ambiguous requirements
- Multiple valid approaches
- Potential breaking changes
- Major architectural decisions

**When to Proceed Independently:**
- Clear, well-defined tasks
- Minor implementation details
- Bug fixes
- Documentation updates

This guide should help maintain consistency and quality throughout the iCloud CLI development process.