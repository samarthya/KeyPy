# KeyPy 🔐

A Python port of [KeePassXC](https://keepassxc.org) - a modern, secure, and open-source password manager.

KeyPy provides both command-line and graphical user interfaces for managing your passwords securely in KeePass (KDBX) format databases.

## Features

### Core Features ✨
- **KDBX Format Support**: Create, open, and manage KeePass databases (KDBX3/KDBX4)
- **Strong Encryption**: Uses industry-standard encryption (AES-256, ChaCha20, Twofish)
- **Password Generator**: Generate strong passwords and passphrases
- **Search Functionality**: Quickly find entries across your database
- **Group Organization**: Organize entries into groups and subgroups
- **Entry Management**: Add, edit, delete, and view password entries

### Command-Line Interface (CLI) 💻
- Create and manage databases
- Add, edit, delete, and search entries
- Generate passwords and passphrases
- Copy passwords to clipboard
- List groups and entries

### Graphical User Interface (GUI) 🖥️
- Modern PyQt6-based interface
- Tree view for groups
- Searchable entry table
- Password visibility toggle
- Entry details panel
- Password generator dialog
- Intuitive menus and toolbar

### Advanced Features 🚀
- **TOTP Support**: Generate time-based one-time passwords (2FA)
- **Password Strength Assessment**: Evaluate password entropy and strength
- **Clipboard Integration**: Copy passwords securely
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

#### List entries
```bash
keypy list mydatabase.kdbx
```

#### Search for entries
```bash
keypy list mydatabase.kdbx -s "github"
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
- **Entry Menu**: Add, edit, and delete entries
- **Tools Menu**: Generate passwords
- **Search Bar**: Filter entries in real-time
- **Group Tree**: Browse and organize entries by groups
- **Entry Table**: View all entries with details
- **Details Panel**: View and copy entry information
- **Password Generator**: Customize password generation options

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
| Browser Integration | ✅ | 🚧 (planned) |
| Auto-Type | ✅ | 🚧 (planned) |
| SSH Agent | ✅ | 🚧 (planned) |
| Database Reports | ✅ | 🚧 (planned) |

## Roadmap

### Phase 1: Foundation ✅
- [x] Core database operations
- [x] Password generator
- [x] CLI interface
- [x] GUI interface
- [x] TOTP support

### Phase 2: Advanced Features 🚧
- [ ] Entry attachments
- [ ] Entry history
- [ ] Database reports (password health, statistics)
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
