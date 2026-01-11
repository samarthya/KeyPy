# KeyPy Examples

This document provides examples of using KeyPy for common password management tasks.

## Table of Contents
- [Database Management](#database-management)
- [Entry Management](#entry-management)
- [Password Generation](#password-generation)
- [Search and Retrieval](#search-and-retrieval)
- [Duplicate Finder](#duplicate-finder)
- [GUI Usage](#gui-usage)

## Database Management

### Create a New Database

```bash
# Create with prompted password
keypy create mydatabase.kdbx

# Create with password on command line (less secure)
keypy create mydatabase.kdbx -p "MyMasterPassword"

# Create with password and key file
keypy create mydatabase.kdbx -p "MyMasterPassword" -k /path/to/keyfile
```

### Open a Database

The database is automatically opened when you perform operations on it. You just need to provide the password:

```bash
keypy list mydatabase.kdbx -p "MyMasterPassword"
```

## Entry Management

### Add a New Entry

```bash
# Add entry with generated password
keypy add mydatabase.kdbx -p "MasterPass" \
  -g "Root/Internet" \
  -t "GitHub" \
  -u "myusername@email.com" \
  --generate

# Add entry with specific password
keypy add mydatabase.kdbx -p "MasterPass" \
  -t "Gmail" \
  -u "me@gmail.com" \
  --pw "MyEmailPassword" \
  --url "https://mail.google.com" \
  --notes "Personal email account"

# Add with custom password length
keypy add mydatabase.kdbx -p "MasterPass" \
  -t "Bank" \
  -u "customer123" \
  --generate \
  -l 32
```

### View Entry Details

```bash
# Show specific entry
keypy show mydatabase.kdbx -p "MasterPass" -t "GitHub"

# Get password only
keypy get mydatabase.kdbx -p "MasterPass" -t "GitHub"

# Copy password to clipboard
keypy get mydatabase.kdbx -p "MasterPass" -t "GitHub" --copy
```

### List All Entries

```bash
# List all entries
keypy list mydatabase.kdbx -p "MasterPass"

# Search for entries
keypy list mydatabase.kdbx -p "MasterPass" -s "github"

# Show passwords in list (be careful!)
keypy list mydatabase.kdbx -p "MasterPass" --show-passwords
```

### Delete an Entry

```bash
# Delete with confirmation
keypy delete mydatabase.kdbx -p "MasterPass" -t "OldAccount"

# Delete without confirmation
keypy delete mydatabase.kdbx -p "MasterPass" -t "OldAccount" --force
```

## Password Generation

### Generate Random Passwords

```bash
# Generate with defaults (16 characters)
keypy generate

# Generate longer password
keypy generate -l 32

# Generate multiple passwords
keypy generate -l 20 -n 5

# Generate and copy to clipboard
keypy generate -l 24 --copy

# Customize character sets
keypy generate -l 20 --no-special      # No special characters
keypy generate -l 20 --no-uppercase    # No uppercase
keypy generate -l 20 --no-digits       # No digits

# Exclude ambiguous characters (il1Lo0O)
keypy generate -l 20 --exclude-ambiguous
```

### Generate Passphrases

```bash
# Generate default passphrase (6 words)
keypy passphrase

# Generate longer passphrase
keypy passphrase -w 8

# Capitalize words
keypy passphrase -w 6 --capitalize

# Custom separator
keypy passphrase -w 5 -s "_"

# Generate and copy
keypy passphrase -w 6 --copy
```

## Search and Retrieval

### Search Entries

```bash
# Search by title
keypy list mydatabase.kdbx -p "MasterPass" -s "git"

# The search is case-insensitive and supports regex
keypy list mydatabase.kdbx -p "MasterPass" -s "^Git.*"
```

### View Groups

```bash
# List all groups
keypy groups mydatabase.kdbx -p "MasterPass"
```

## Duplicate Finder

KeyPy includes a powerful duplicate entry finder and optimizer to help maintain a clean password database.

### Find Duplicates

#### Basic Usage

```bash
# Find and display duplicate entries
keypy find-duplicates mydatabase.kdbx -p "MasterPass"
```

This will scan your database and provide a detailed report including:
- Total entries scanned
- Number of duplicate groups
- Details of each duplicate entry
- Warnings for entries with different passwords

#### Example Output

```
================================================================================
Duplicate Entry Report
================================================================================

Statistics:
  Total entries scanned:    150
  Duplicate groups found:   3
  Total duplicate entries:  8
  Redundant entries:        5

⚠ Warning: 1 group(s) have different passwords!

Duplicate Groups:

────────────────────────────────────────────────────────────────────────────────
Group 1: https://github.com - user@example.com
  Found 3 duplicate entries:

  1. GitHub - Personal
     Username: user@example.com
     URL:      https://github.com
     Group:    Root/Personal
     Modified: 2024-01-15 10:30:00

  2. GitHub - Work
     Username: user@example.com
     URL:      https://www.github.com
     Group:    Root/Work
     Modified: 2024-02-20 14:15:00

  3. GitHub Old
     Username: user@example.com
     URL:      https://github.com
     Group:    Root
     Modified: 2023-11-10 09:00:00
```

### JSON Output

```bash
# Export report as JSON
keypy find-duplicates mydatabase.kdbx -p "MasterPass" --json

# Save JSON report to file
keypy find-duplicates mydatabase.kdbx -p "MasterPass" --json --output duplicates.json
```

Example JSON output:
```json
{
  "total_entries": 150,
  "duplicate_groups": 3,
  "total_duplicates": 8,
  "redundant_entries": 5,
  "groups": [
    {
      "url": "https://github.com",
      "username": "user@example.com",
      "count": 3,
      "has_different_passwords": false,
      "entries": [
        {
          "title": "GitHub - Personal",
          "username": "user@example.com",
          "url": "https://github.com",
          "group": "Personal",
          "modified": "2024-01-15T10:30:00+00:00"
        }
      ]
    }
  ]
}
```

### Save Report to File

```bash
# Save human-readable report to text file
keypy find-duplicates mydatabase.kdbx -p "MasterPass" --output report.txt
```

### Interactive Optimization

The optimizer helps you clean up duplicate entries interactively:

```bash
# Start interactive optimization
keypy optimize mydatabase.kdbx -p "MasterPass"
```

#### Optimization Workflow

1. **Automatic Backup**: Creates a timestamped backup (e.g., `mydatabase.kdbx.backup.20240115_143000.kdbx`)
2. **Review Each Group**: Shows all duplicate entries with full details
3. **User Selection**: Choose which entry to keep
4. **Confirmation**: Confirms before deleting any entries
5. **Audit Log**: Creates a log file with all actions taken

#### Interactive Options

For each duplicate group, you can:
- **1-N**: Keep entry number N and delete all others
- **s**: Skip this group (keep all duplicates)
- **q**: Quit optimization without making changes

#### Example Session

```
================================================================================
Interactive Duplicate Optimization
================================================================================

────────────────────────────────────────────────────────────────────────────────
Group 1 of 3
URL: https://github.com
Username: user@example.com

Duplicate entries:

  [1] GitHub - Personal
      Username: user@example.com
      URL:      https://github.com
      Group:    Root/Personal
      Modified: 2024-01-15 10:30:00
      Notes:    My personal GitHub account

  [2] GitHub - Work
      Username: user@example.com
      URL:      https://www.github.com
      Group:    Root/Work
      Modified: 2024-02-20 14:15:00
      Notes:    Work account, expires 2025

  [3] GitHub Old
      Username: user@example.com
      URL:      https://github.com
      Group:    Root
      Modified: 2023-11-10 09:00:00

Options:
  1-N : Keep entry N and mark others for deletion
  s   : Skip this group (keep all duplicates)
  q   : Quit optimization

Your choice: 2

✓ Will keep: GitHub - Work
  ✗ Will delete: GitHub - Personal
  ✗ Will delete: GitHub Old
```

### Dry-Run Mode

Preview what would be optimized without making any changes:

```bash
# Preview optimization without modifying database
keypy optimize mydatabase.kdbx -p "MasterPass" --dry-run
```

Dry-run mode:
- Shows exactly what would happen
- No backup is created
- No entries are deleted
- Perfect for reviewing duplicates before committing

### Safety Features

The duplicate optimizer includes multiple safety features:

1. **Automatic Backups**: Creates timestamped backup before any changes
   - Format: `database.kdbx.backup.YYYYMMDD_HHMMSS.kdbx`
   - Can restore by opening the backup file

2. **Audit Logs**: Records all actions taken
   - Format: `database.kdbx.audit.YYYYMMDD_HHMMSS.log`
   - Includes timestamp, actions, and deleted entries

3. **Password Warnings**: Alerts when duplicates have different passwords
   - Helps avoid accidentally merging different accounts
   - Shows warning prominently in red

4. **Explicit Confirmation**: Never deletes without user confirmation
   - Interactive selection for each group
   - Final confirmation before applying changes

5. **Dry-Run Mode**: Preview changes safely

### Common Scenarios

#### Scenario 1: Merge Accounts After URL Change

If a service changed its URL (e.g., twitter.com → x.com):

```bash
# Find duplicates to see both entries
keypy find-duplicates mydatabase.kdbx -p "MasterPass"

# Optimize to keep only the current URL
keypy optimize mydatabase.kdbx -p "MasterPass"
# Select the entry with the new URL to keep
```

#### Scenario 2: Clean Up After Import

After importing from another password manager:

```bash
# Check for duplicates
keypy find-duplicates mydatabase.kdbx -p "MasterPass" --json --output import-duplicates.json

# Review the JSON report
cat import-duplicates.json

# Optimize with dry-run first
keypy optimize mydatabase.kdbx -p "MasterPass" --dry-run

# Then optimize for real
keypy optimize mydatabase.kdbx -p "MasterPass"
```

#### Scenario 3: Audit Duplicate Entries

Generate a report for review without making changes:

```bash
# Generate detailed report
keypy find-duplicates mydatabase.kdbx -p "MasterPass" --output audit-report.txt

# Review the report
less audit-report.txt

# Optionally generate JSON for analysis
keypy find-duplicates mydatabase.kdbx -p "MasterPass" --json --output audit-data.json
```

### View Groups

## GUI Usage

### Launch the GUI

```bash
# Start the GUI application
keypy-gui

# Or run directly with Python
python -m keypy.gui.main
```

### GUI Features

#### Main Window
- **Group Tree** (left panel): Browse and organize entries by groups
- **Entry Table** (center): View all entries with title, username, and URL
- **Details Panel** (bottom): View and copy selected entry details
- **Search Bar**: Filter entries in real-time

#### Menus

**File Menu**:
- New Database (Ctrl+N)
- Open Database (Ctrl+O)
- Save Database (Ctrl+S)
- Exit (Ctrl+Q)

**Entry Menu**:
- Add Entry (Ctrl+E)
- Edit Entry
- Delete Entry (Delete key)

**Tools Menu**:
- Generate Password (Ctrl+G)

**Help Menu**:
- About

#### Keyboard Shortcuts
- `Ctrl+N`: Create new database
- `Ctrl+O`: Open database
- `Ctrl+S`: Save database
- `Ctrl+E`: Add new entry
- `Ctrl+G`: Generate password
- `Delete`: Delete selected entry
- `Ctrl+Q`: Exit application

#### Working with Entries

1. **Add Entry**:
   - Click "Add Entry" in toolbar or press Ctrl+E
   - Fill in title, username, password, URL, and notes
   - Click "Generate" to create a strong password
   - Click "OK" to save

2. **Edit Entry**:
   - Select entry in the table
   - Click "Edit Entry" or double-click the entry
   - Modify fields as needed
   - Click "OK" to save

3. **View Password**:
   - Select entry in the table
   - Password appears in details panel (hidden by default)
   - Click "Show" to reveal password
   - Click "Copy" to copy to clipboard

4. **Search**:
   - Type in the search bar
   - Results are filtered in real-time
   - Search applies to entry titles

5. **Organize with Groups**:
   - When adding/editing entries, specify group path
   - Groups are created automatically if they don't exist
   - Use format: "Root/Category/Subcategory"

## Advanced Usage

### Using Key Files

```bash
# Create database with key file
keypy create mydatabase.kdbx -p "MasterPass" -k /path/to/keyfile

# Use key file when accessing database
keypy list mydatabase.kdbx -p "MasterPass" -k /path/to/keyfile
```

### Organizing with Groups

Groups help organize your entries. Use forward slashes to create nested groups:

```bash
# Add to specific group
keypy add mydatabase.kdbx -p "MasterPass" \
  -g "Root/Work/Development" \
  -t "Work GitHub" \
  -u "work@company.com" \
  --generate

# Add to different categories
keypy add mydatabase.kdbx -p "MasterPass" -g "Root/Personal/Social" ...
keypy add mydatabase.kdbx -p "MasterPass" -g "Root/Banking/Primary" ...
keypy add mydatabase.kdbx -p "MasterPass" -g "Root/Email/Personal" ...
```

## Python API Usage

You can also use KeyPy as a Python library:

```python
from keypy.core.database import DatabaseManager
from keypy.core.password_generator import PasswordGenerator

# Create and manage database
db = DatabaseManager()
db.create('mydatabase.kdbx', 'password')

# Add entry
db.add_entry(
    group_path='Root/Internet',
    title='GitHub',
    username='user@example.com',
    password='SecurePassword123!',
    url='https://github.com',
    notes='My GitHub account'
)

# Generate password
gen = PasswordGenerator()
password = gen.generate(length=20)
print(f"Generated: {password}")

# Assess password strength
strength = gen.assess_strength(password)
print(f"Strength: {strength['strength']} ({strength['entropy']:.1f} bits)")

# Generate passphrase
passphrase = gen.generate_passphrase(word_count=6)
print(f"Passphrase: {passphrase}")
```

## Tips and Best Practices

1. **Strong Master Password**: Use a long, unique master password with mixed character types
2. **Key Files**: Consider using a key file for additional security
3. **Regular Backups**: Keep encrypted backups of your database in multiple locations
4. **Group Organization**: Use groups to organize entries logically
5. **Unique Passwords**: Generate unique passwords for each account
6. **Password Length**: Use at least 16 characters for important accounts
7. **Passphrases**: Consider passphrases for memorable but secure passwords
8. **Never Share**: Never share your master password or database file
9. **Regular Duplicate Checks**: Run `find-duplicates` periodically to keep your database clean
10. **Safe Optimization**: Always use `--dry-run` first before optimizing duplicates
11. **Keep Backups**: The optimizer creates automatic backups, but keep manual backups too

## Troubleshooting

### Can't Open Database
- Check that you're using the correct password
- Verify the database file path
- Ensure the file isn't corrupted

### Permission Denied
- Check file permissions on the database file
- Ensure you have write access to the directory

### Clipboard Not Working
- pyperclip may require additional setup on some systems
- On Linux, you may need to install: `sudo apt-get install xclip`

## Getting Help

For more information:
- Run `keypy --help` for CLI help
- Run `keypy COMMAND --help` for command-specific help
- Check the [README.md](README.md) for installation and setup
- Open an issue on [GitHub](https://github.com/samarthya/KeyPy/issues)
