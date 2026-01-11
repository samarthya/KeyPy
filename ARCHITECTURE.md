# KeyPy Architecture

This document describes the architecture and design decisions of KeyPy.

## Overview

KeyPy is a Python port of KeePassXC, designed to provide secure password management with both CLI and GUI interfaces. The application follows a modular architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User Interfaces                      │
├──────────────────────┬──────────────────────────────────┤
│   CLI (Click)        │        GUI (PyQt6)              │
│   - Commands         │        - Main Window            │
│   - Arguments        │        - Dialogs                │
│   - Output           │        - Widgets                │
└──────────────────────┴──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    Core Layer                            │
├──────────────────────┬──────────────────────────────────┤
│  DatabaseManager     │    PasswordGenerator            │
│  - KDBX I/O          │    - Random passwords           │
│  - CRUD operations   │    - Passphrases                │
│  - Groups            │    - Strength assessment        │
└──────────────────────┴──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 Utility Layer                            │
├──────────────────────┬──────────────────────────────────┤
│     TOTP             │       Clipboard                  │
│  - Token gen         │    - Copy/paste                  │
│  - Verification      │                                  │
└──────────────────────┴──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              External Dependencies                       │
├─────────────────────────────────────────────────────────┤
│  PyKeePass - KDBX format handling                       │
│  Cryptography - Encryption primitives                   │
│  Argon2 - Key derivation                                │
│  PyQt6 - GUI framework                                  │
│  Click - CLI framework                                  │
└─────────────────────────────────────────────────────────┘
```

## Module Structure

### Core Modules

#### `keypy.core.database`
**Purpose**: Manages KeePass database operations

**Key Classes**:
- `DatabaseManager`: Main database interface

**Responsibilities**:
- Create/open/save databases
- CRUD operations on entries
- Group management
- Search functionality

**Dependencies**:
- `pykeepass`: For KDBX format handling
- `pathlib`: For file path management

**Design Decisions**:
- Uses PyKeePass library to avoid reimplementing KDBX format
- Provides higher-level API than PyKeePass for easier use
- Maintains single database instance per manager

#### `keypy.core.password_generator`
**Purpose**: Generate secure passwords and passphrases

**Key Classes**:
- `PasswordGenerator`: Password generation and assessment

**Responsibilities**:
- Random password generation
- Passphrase generation
- Entropy calculation
- Strength assessment

**Dependencies**:
- `random`: For cryptographically secure random numbers
- `string`: For character sets
- `math`: For entropy calculations

**Design Decisions**:
- Uses system random for cryptographic security
- Configurable character sets
- EFF wordlist subset for passphrases
- Entropy-based strength assessment

### CLI Module

#### `keypy.cli.main`
**Purpose**: Command-line interface

**Structure**:
- Click-based command groups
- Global database manager instance
- Command-specific handlers

**Commands**:
- `create`: Create new database
- `add`: Add entry
- `list`: List entries
- `show`: Show entry details
- `get`: Get password
- `delete`: Delete entry
- `generate`: Generate password
- `passphrase`: Generate passphrase
- `groups`: List groups

**Design Decisions**:
- Uses Click for argument parsing and validation
- Colorized output with colorama
- Password prompts for security
- Clipboard integration optional

### GUI Module

#### `keypy.gui.main`
**Purpose**: Graphical user interface

**Key Classes**:
- `KeyPyMainWindow`: Main application window
- `EntryDialog`: Add/edit entry dialog
- `PasswordGeneratorDialog`: Password generation dialog

**Components**:
- Menu bar with File/Entry/Tools/Help menus
- Toolbar with quick actions
- Group tree (left panel)
- Entry table (center panel)
- Entry details (bottom panel)
- Search bar

**Design Decisions**:
- PyQt6 for modern GUI framework
- Splitter for resizable panels
- Signal/slot pattern for events
- Modal dialogs for data entry
- Real-time search filtering

### Utility Modules

#### `keypy.utils.totp`
**Purpose**: TOTP token generation and verification

**Key Classes**:
- `TOTPManager`: Static methods for TOTP operations

**Responsibilities**:
- Generate TOTP secrets
- Generate time-based tokens
- Verify tokens
- Create provisioning URIs

**Dependencies**:
- `pyotp`: For TOTP implementation

## Data Flow

### Creating an Entry (CLI)

```
User Input (CLI)
    │
    ▼
Click Command Handler
    │
    ▼
DatabaseManager.open()
    │
    ▼
DatabaseManager.add_entry()
    │
    ▼
PyKeePass.add_entry()
    │
    ▼
PyKeePass.save()
    │
    ▼
Encrypted KDBX File
```

### Opening Database (GUI)

```
User Action (File → Open)
    │
    ▼
QFileDialog (select file)
    │
    ▼
QInputDialog (password)
    │
    ▼
DatabaseManager.open()
    │
    ▼
PyKeePass.__init__()
    │
    ▼
Load and decrypt database
    │
    ▼
MainWindow._load_database()
    │
    ▼
Populate UI (groups, entries)
```

## Security Architecture

### Encryption

**At Rest**:
- KDBX format with AES-256 encryption
- Argon2 key derivation function
- Master password + optional key file

**In Memory**:
- PyKeePass manages encryption/decryption
- No plaintext storage beyond memory
- Database saved on modifications

**Key Derivation**:
```
Master Password + Salt
        │
        ▼
    Argon2 KDF
        │
        ▼
  Master Key (256-bit)
        │
        ▼
   AES-256 Encryption
        │
        ▼
  Encrypted Database
```

### Password Generation

- Uses `random.choice()` which uses OS entropy
- Configurable character sets
- Excludes ambiguous characters optionally
- Entropy calculation for strength assessment

### Clipboard Security

- Uses pyperclip for clipboard access
- No automatic clearing (user responsibility)
- Optional clipboard operations

## Database Format

### KDBX Structure

```
KDBX File
├── Header (unencrypted)
│   ├── Cipher (AES-256)
│   ├── Compression (gzip)
│   ├── Master seed
│   └── Transform rounds
│
└── Encrypted Payload
    ├── Meta (database info)
    │   ├── Database name
    │   ├── Description
    │   └── Settings
    │
    └── Root Group
        ├── Subgroups
        │   └── Entries
        │       ├── Title
        │       ├── Username
        │       ├── Password
        │       ├── URL
        │       ├── Notes
        │       └── Timestamps
        └── Entries
```

## Extension Points

### Adding New Features

#### New CLI Command

```python
@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--option", help="Option description")
def new_command(database, option):
    """Command description."""
    # Implementation
    pass
```

#### New GUI Dialog

```python
class NewDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        # Dialog UI setup
        pass
```

#### New Core Feature

```python
# In keypy/core/new_feature.py
class NewFeature:
    def __init__(self):
        pass
    
    def do_something(self):
        pass
```

## Performance Considerations

### Database Operations

- PyKeePass loads entire database into memory
- Save operations write entire database
- For large databases (>10MB), operations may be slower
- No incremental save/load currently

### GUI Responsiveness

- Database operations on main thread
- Large databases may cause UI freeze
- Future: Move to background threads

### Memory Usage

- Entire database in memory
- Entry objects cached
- Moderate memory footprint (<100MB typical)

## Testing Strategy

### Unit Tests

- Test individual functions/methods
- Mock external dependencies
- Focus on core logic

### Integration Tests

- Test module interactions
- Use temporary databases
- Verify end-to-end flows

### Test Structure

```
tests/
├── test_database.py      # Database operations
├── test_password_generator.py  # Password generation
└── test_totp.py         # TOTP functionality
```

## Future Architecture

### Planned Enhancements

1. **Plugin System**
   - Allow third-party extensions
   - Plugin API for custom features

2. **Async Operations**
   - Background database operations
   - Non-blocking GUI

3. **Cloud Sync**
   - Optional cloud backup
   - Conflict resolution

4. **Browser Integration**
   - Native messaging host
   - Browser extension communication

5. **Auto-Type**
   - Platform-specific keyboard input
   - Custom auto-type sequences

## Dependencies Rationale

### PyKeePass
- Mature KDBX implementation
- Active maintenance
- Python-native

### PyQt6
- Cross-platform GUI
- Rich widget set
- Modern and actively maintained

### Click
- Intuitive CLI framework
- Automatic help generation
- Good validation

### Cryptography
- Industry-standard crypto library
- Well-audited
- Comprehensive primitives

## Build and Distribution

### Package Structure

```
KeyPy/
├── setup.py           # Package configuration
├── requirements.txt   # Dependencies
├── src/keypy/        # Source code
└── tests/            # Test suite
```

### Installation Methods

1. **Development**: `pip install -e .`
2. **User**: `pip install keypy` (when published)
3. **Source**: `python setup.py install`

### Entry Points

```python
entry_points={
    "console_scripts": [
        "keypy=keypy.cli.main:cli",
        "keypy-gui=keypy.gui.main:main",
    ],
}
```

## Compatibility

### Python Versions
- Minimum: Python 3.8
- Tested: 3.8, 3.9, 3.10, 3.11, 3.12

### Platforms
- Linux: Full support
- macOS: Full support
- Windows: Full support

### KDBX Versions
- KDBX3: Full support (via PyKeePass)
- KDBX4: Full support (via PyKeePass)
- KeePass 1.x: Not supported

## References

- [KeePassXC Documentation](https://keepassxc.org/docs/)
- [KDBX Format Specification](https://keepass.info/help/kb/kdbx_4.html)
- [PyKeePass Documentation](https://github.com/libkeepass/pykeepass)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
