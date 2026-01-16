# KeyPy 🔐

A Python port of [KeePassXC](https://keepassxc.org) - a modern, secure, and open-source password manager.

KeyPy provides both command-line and graphical user interfaces for managing your passwords securely in KeePass (KDBX) format databases.

## Features

### Core Features ✨
- **KDBX Format Support**: Create, open, and manage KeePass databases (KDBX3/KDBX4)
- **Strong Encryption**: Uses industry-standard encryption (AES-256, ChaCha20, Twofish)
- **Password Generator**: Generate strong passwords and passphrases
- **Search Functionality**: Quickly find entries across your database (including tags)
- **Group Organization**: Organize entries into groups and subgroups
- **Entry Management**: Add, edit, delete, and view password entries
- **Tags & Icons**: Label entries with tags for better organization and assign icons
- **Import/Export**: Import and export entries in CSV format or merge KDBX databases

### Command-Line Interface (CLI) 💻
- Create and manage databases
- Add, edit, delete, and search entries with tags
- Generate passwords and passphrases
- Copy passwords to clipboard
- List groups and entries
- Find and optimize duplicate entries
- Export entries to CSV format
- Import entries from CSV or KDBX databases

### Graphical User Interface (GUI) 🖥️
- Modern PyQt6-based interface
- Tree view for groups
- Searchable entry table with tags column
- Password visibility toggle
- Entry details panel with tags display
- Password generator dialog
- Intuitive menus and toolbar
- Auto-save prompts for unsaved changes
- CSV and KDBX import/export dialogs
- Safe deletion with recycle bin option

### Advanced Features 🚀
- **TOTP Support**: Generate time-based one-time passwords (2FA)
- **Password Strength Assessment**: Evaluate password entropy and strength
- **Clipboard Integration**: Copy passwords securely
- **Duplicate Finder**: Identify and manage duplicate password entries
- **Database Optimizer**: Interactively clean up duplicate entries with automatic backups
- **Safe Deletion**: Move entries to recycle bin instead of permanent deletion
- **Tags & Labels**: Organize entries with custom tags for easy searching
- **Entry Icons**: Visual indicators for entries (68 built-in icons)
- **CSV Import/Export**: Backup or migrate entries using CSV format
- **KDBX Import**: Merge entries from other KeePass databases with duplicate detection
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### From Source

```bash
# Clone the repository
git clone https://github.com/samarthya/KeyPy.git
cd KeyPy

# Install dependencies
pip install -r requirements.txt

# Install KeyPy
pip install -e .
```

## Usage

### Command-Line Interface

#### Create a new database
```bash
keypy create mydatabase.kdbx
```

#### Add an entry
```bash
keypy add mydatabase.kdbx -t "GitHub" -u "user@example.com" --generate
```

#### Add an entry with tags and icon
```bash
keypy add mydatabase.kdbx -t "GitHub" -u "user@example.com" --generate \
  --tags "work,dev,important" --icon "1" --url "https://github.com"
```

#### List entries
```bash
keypy list mydatabase.kdbx
```

#### Search for entries (searches title, username, URL, and tags)
```bash
keypy list mydatabase.kdbx -s "github"

# Search by tag
keypy list mydatabase.kdbx -s "work"
```

#### Get a password
```bash
keypy get mydatabase.kdbx -t "GitHub" --copy
```

#### Generate a password
```bash
keypy generate -l 20 --copy
```

#### Generate a passphrase
```bash
keypy passphrase -w 6 --capitalize
```

#### Delete an entry
```bash
keypy delete mydatabase.kdbx -t "GitHub"
```

#### List groups
```bash
keypy groups mydatabase.kdbx
```

#### Find duplicate entries
```bash
# Display duplicate entries report
keypy find-duplicates mydatabase.kdbx

# Output report in JSON format
keypy find-duplicates mydatabase.kdbx --json

# Save report to a file
keypy find-duplicates mydatabase.kdbx --output report.txt
```

#### Optimize duplicate entries
```bash
# Interactive optimization with backup
keypy optimize mydatabase.kdbx

# Preview changes without modifying database
keypy optimize mydatabase.kdbx --dry-run
```

#### Export entries to CSV
```bash
# Export without passwords (safer)
keypy export-csv mydatabase.kdbx exported_entries.csv

# Export with passwords (WARNING: CSV is not encrypted!)
keypy export-csv mydatabase.kdbx exported_entries.csv --include-passwords
```

#### Import entries from CSV
```bash
# Import entries from CSV file
keypy import-csv mydatabase.kdbx entries.csv

# Import to a specific group
keypy import-csv mydatabase.kdbx entries.csv --group "Imported"
```

#### Import entries from another KDBX database
```bash
# Merge another database (duplicates are skipped)
keypy import-kdbx mydatabase.kdbx source.kdbx

# Will prompt for passwords for both databases
```

### Graphical User Interface

Launch the GUI application:

```bash
keypy-gui
```

Or run directly:

```bash
python -m keypy.gui.main
```

#### GUI Features:
- **File Menu**: Create, open, and save databases
  - Import from CSV or KDBX
  - Export to CSV
- **Entry Menu**: Add, edit, and delete entries
  - Assign tags and icons to entries
  - Safe deletion with recycle bin option
- **Tools Menu**: Generate passwords
- **Search Bar**: Filter entries in real-time (searches title, username, URL, and tags)
- **Group Tree**: Browse and organize entries by groups
- **Entry Table**: View all entries with details including tags
- **Details Panel**: View and copy entry information
  - Display tags for each entry
  - Toggle password visibility
- **Auto-save prompts**: Get notified when closing with unsaved changes
- **Password Generator**: Customize password generation options

## Duplicate Finder & Optimizer

KeyPy includes a powerful duplicate entry finder and optimizer to help maintain a clean password database.

### Features

- **Smart Detection**: Identifies duplicates based on URL and username
- **URL Normalization**: Recognizes similar URLs (e.g., `https://example.com` and `https://www.example.com`)
- **Case-Insensitive Matching**: Matches usernames regardless of case
- **Password Warnings**: Alerts when entries have the same URL/username but different passwords
- **Multiple Output Formats**: View reports in console or export as JSON
- **Interactive Optimization**: Safely remove duplicates with user confirmation
- **Automatic Backups**: Creates timestamped backups before making changes
- **Audit Logging**: Tracks all optimization operations
- **Dry-Run Mode**: Preview changes without modifying the database

### Usage Examples

#### Find Duplicates

```bash
# Display a detailed report of duplicate entries
keypy find-duplicates mydatabase.kdbx

# Output as JSON for programmatic processing
keypy find-duplicates mydatabase.kdbx --json

# Save report to a file
keypy find-duplicates mydatabase.kdbx --output duplicates_report.txt
```

The report includes:
- Total entries scanned
- Number of duplicate groups found
- Total redundant entries
- Detailed information for each duplicate group
- Warnings for entries with different passwords

#### Optimize Database

```bash
# Interactive optimization mode
keypy optimize mydatabase.kdbx

# Preview changes without modifying database
keypy optimize mydatabase.kdbx --dry-run
```

The optimizer will:
1. Scan for duplicate entries
2. Present each duplicate group interactively
3. Allow you to select which entry to keep
4. Create automatic backup before deletion
5. Generate an audit log of all actions
6. Require explicit confirmation before deletion

### Safety Features

- ✅ **Never automatically deletes** - always requires user confirmation
- ✅ **Automatic backups** - creates timestamped backup files
- ✅ **Audit logs** - records all optimization operations
- ✅ **Dry-run mode** - preview changes safely
- ✅ **Password warnings** - alerts about entries with different passwords

## Project Structure

```
KeyPy/
├── src/
│   └── keypy/
│       ├── core/              # Core functionality
│       │   ├── database.py    # Database management
│       │   └── password_generator.py  # Password generation
│       ├── cli/               # Command-line interface
│       │   └── main.py        # CLI application
│       ├── gui/               # Graphical interface
│       │   └── main.py        # GUI application
│       └── utils/             # Utility modules
│           └── totp.py        # TOTP support
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
├── setup.py                  # Package setup
└── README.md                 # Documentation
```

## Security

KeyPy uses the same security standards as KeePassXC:
- **AES-256 encryption** for database files
- **Argon2** key derivation function (KDF)
- **Master password** protection
- Optional **key file** support
- **Secure password generation** with cryptographic randomness

**Important Security Notes:**
- Always use a strong master password
- Keep your database file secure
- Never share your master password or key file
- Regularly backup your database

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

## Comparison with KeePassXC

KeyPy aims to replicate the core functionality of KeePassXC in Python:

| Feature | KeePassXC | KeyPy |
|---------|-----------|-------|
| KDBX Format Support | ✅ | ✅ |
| Password Generator | ✅ | ✅ |
| CLI Interface | ✅ | ✅ |
| GUI Interface | ✅ | ✅ |
| Search Functionality | ✅ | ✅ |
| Group Organization | ✅ | ✅ |
| TOTP Support | ✅ | ✅ (basic) |
| Duplicate Finder | ✅ | ✅ |
| Browser Integration | ✅ | 🚧 (planned) |
| Auto-Type | ✅ | 🚧 (planned) |
| SSH Agent | ✅ | 🚧 (planned) |
| Database Reports | ✅ | ✅ (duplicates) |

## Roadmap

### Phase 1: Foundation ✅
- [x] Core database operations
- [x] Password generator
- [x] CLI interface
- [x] GUI interface
- [x] TOTP support
- [x] Duplicate finder and optimizer

### Phase 2: Advanced Features 🚧
- [ ] Entry attachments
- [ ] Entry history
- [x] Database reports (duplicate detection)
- [ ] Additional database reports (password health, statistics)
- [ ] Import/Export (CSV, XML, HTML)
- [ ] Auto-type functionality

### Phase 3: Integration 📋
- [ ] Browser integration
- [ ] SSH agent integration
- [ ] Cloud storage sync
- [ ] Mobile companion app

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [KeePassXC](https://keepassxc.org) - The original inspiration and reference implementation
- [PyKeePass](https://github.com/libkeepass/pykeepass) - Python library for KeePass database access
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

## Disclaimer

KeyPy is an independent project and is not affiliated with or endorsed by the KeePassXC team. KeePassXC is a registered trademark of the KeePassXC Team.

## Support

For issues, questions, or suggestions, please open an issue on [GitHub](https://github.com/samarthya/KeyPy/issues).
