"""Command-line interface for KeyPy."""
import click
import sys
import os
import json
from pathlib import Path
from getpass import getpass
from datetime import datetime
import pyperclip
from colorama import init, Fore, Style

from keypy.core.database import DatabaseManager
from keypy.core.password_generator import PasswordGenerator
from keypy.core.duplicate_finder import DuplicateFinder

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Global database manager
db_manager = DatabaseManager()
password_generator = PasswordGenerator()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """KeyPy - A Python port of KeePassXC password manager.
    
    Manage your passwords securely from the command line.
    """
    pass


@cli.command()
@click.argument("database", type=click.Path())
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
def create(database, password, keyfile):
    """Create a new KeePass database."""
    if not password:
        password = getpass("Enter master password: ")
        password_confirm = getpass("Confirm master password: ")
        
        if password != password_confirm:
            click.echo(f"{Fore.RED}Passwords do not match!")
            sys.exit(1)
    
    if os.path.exists(database):
        if not click.confirm(f"Database {database} already exists. Overwrite?"):
            sys.exit(0)
        os.remove(database)
    
    click.echo(f"Creating database: {database}")
    
    if db_manager.create(database, password, keyfile):
        click.echo(f"{Fore.GREEN}Database created successfully!")
    else:
        click.echo(f"{Fore.RED}Failed to create database")
        sys.exit(1)


@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--group", "-g", default="Root", help="Group path (default: Root)")
@click.option("--title", "-t", required=True, help="Entry title")
@click.option("--username", "-u", required=True, help="Username")
@click.option("--password-value", "--pw", help="Password (will generate if not provided)")
@click.option("--url", help="URL")
@click.option("--notes", "-n", help="Notes")
@click.option("--tags", help="Tags (comma-separated)")
@click.option("--icon", help="Icon number (0-68)")
@click.option("--generate", is_flag=True, help="Generate password")
@click.option("--length", "-l", default=16, help="Generated password length")
def add(database, password, keyfile, group, title, username, password_value, url, notes, tags, icon, generate, length):
    """Add a new entry to the database."""
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    # Generate password if requested or not provided
    if generate or not password_value:
        password_value = password_generator.generate(length=length)
        click.echo(f"{Fore.CYAN}Generated password: {password_value}")
    
    if db_manager.add_entry(group, title, username, password_value, url, notes, tags, icon):
        click.echo(f"{Fore.GREEN}Entry '{title}' added successfully!")
    else:
        click.echo(f"{Fore.RED}Failed to add entry")
        sys.exit(1)


@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--search", "-s", help="Search term")
@click.option("--group", "-g", help="Filter by group")
@click.option("--show-passwords", is_flag=True, help="Show passwords in output")
def list(database, password, keyfile, search, group, show_passwords):
    """List entries in the database."""
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    entries = db_manager.get_entries(search=search)
    
    if not entries:
        click.echo("No entries found")
        return
    
    click.echo(f"\n{Fore.CYAN}{'Title':<30} {'Username':<20} {'URL':<40}")
    click.echo("-" * 90)
    
    for entry in entries:
        title = entry.title[:28] if len(entry.title) > 28 else entry.title
        username = entry.username[:18] if entry.username and len(entry.username) > 18 else (entry.username or "")
        url = entry.url[:38] if entry.url and len(entry.url) > 38 else (entry.url or "")
        
        click.echo(f"{title:<30} {username:<20} {url:<40}")
        
        if show_passwords:
            click.echo(f"  {Fore.YELLOW}Password: {entry.password}")


@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--title", "-t", required=True, help="Entry title")
def show(database, password, keyfile, title):
    """Show details of a specific entry."""
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    entries = db_manager.find_entries(title=title, regex=False)
    
    if not entries:
        click.echo(f"{Fore.RED}Entry '{title}' not found")
        sys.exit(1)
    
    if len(entries) > 1:
        click.echo(f"{Fore.YELLOW}Multiple entries found. Showing first match.")
    
    entry = entries[0]
    
    click.echo(f"\n{Fore.CYAN}Entry Details:")
    click.echo(f"  Title:    {entry.title}")
    click.echo(f"  Username: {entry.username or '(none)'}")
    click.echo(f"  Password: {entry.password}")
    click.echo(f"  URL:      {entry.url or '(none)'}")
    click.echo(f"  Notes:    {entry.notes or '(none)'}")
    click.echo(f"  Group:    {entry.group.name if entry.group else '(none)'}")
    click.echo(f"  Modified: {entry.mtime}")


@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--title", "-t", required=True, help="Entry title")
@click.option("--copy", "-c", is_flag=True, help="Copy password to clipboard")
def get(database, password, keyfile, title, copy):
    """Get password for a specific entry."""
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    entries = db_manager.find_entries(title=title, regex=False)
    
    if not entries:
        click.echo(f"{Fore.RED}Entry '{title}' not found")
        sys.exit(1)
    
    if len(entries) > 1:
        click.echo(f"{Fore.YELLOW}Multiple entries found. Using first match.")
    
    entry = entries[0]
    
    if copy:
        try:
            pyperclip.copy(entry.password)
            click.echo(f"{Fore.GREEN}Password copied to clipboard!")
        except Exception as e:
            click.echo(f"{Fore.RED}Failed to copy to clipboard: {e}")
            click.echo(f"Password: {entry.password}")
    else:
        click.echo(f"Password: {entry.password}")


@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--title", "-t", required=True, help="Entry title to delete")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(database, password, keyfile, title, force):
    """Delete an entry from the database."""
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    entries = db_manager.find_entries(title=title, regex=False)
    
    if not entries:
        click.echo(f"{Fore.RED}Entry '{title}' not found")
        sys.exit(1)
    
    if len(entries) > 1:
        click.echo(f"{Fore.YELLOW}Multiple entries found. Deleting first match.")
    
    entry = entries[0]
    
    if not force:
        if not click.confirm(f"Delete entry '{entry.title}'?"):
            click.echo("Cancelled")
            return
    
    if db_manager.delete_entry(entry):
        click.echo(f"{Fore.GREEN}Entry '{title}' deleted successfully!")
    else:
        click.echo(f"{Fore.RED}Failed to delete entry")
        sys.exit(1)


@cli.command()
@click.option("--length", "-l", default=16, help="Password length")
@click.option("--no-lowercase", is_flag=True, help="Exclude lowercase letters")
@click.option("--no-uppercase", is_flag=True, help="Exclude uppercase letters")
@click.option("--no-digits", is_flag=True, help="Exclude digits")
@click.option("--no-special", is_flag=True, help="Exclude special characters")
@click.option("--exclude-ambiguous", is_flag=True, help="Exclude ambiguous characters")
@click.option("--copy", "-c", is_flag=True, help="Copy to clipboard")
@click.option("--count", "-n", default=1, help="Number of passwords to generate")
def generate(length, no_lowercase, no_uppercase, no_digits, no_special, exclude_ambiguous, copy, count):
    """Generate random passwords."""
    for i in range(count):
        pwd = password_generator.generate(
            length=length,
            use_lowercase=not no_lowercase,
            use_uppercase=not no_uppercase,
            use_digits=not no_digits,
            use_special=not no_special,
            exclude_ambiguous=exclude_ambiguous
        )
        
        if copy and count == 1:
            try:
                pyperclip.copy(pwd)
                click.echo(f"{Fore.GREEN}Password: {pwd} (copied to clipboard)")
            except Exception as e:
                click.echo(f"{Fore.YELLOW}Password: {pwd} (clipboard copy failed: {e})")
        else:
            # Show strength assessment
            strength = password_generator.assess_strength(pwd)
            strength_color = Fore.GREEN if strength['score'] >= 4 else Fore.YELLOW if strength['score'] >= 3 else Fore.RED
            click.echo(f"{pwd}  {strength_color}({strength['strength']}, {strength['entropy']:.1f} bits)")


@cli.command()
@click.option("--words", "-w", default=6, help="Number of words")
@click.option("--separator", "-s", default="-", help="Word separator")
@click.option("--capitalize", is_flag=True, help="Capitalize words")
@click.option("--copy", "-c", is_flag=True, help="Copy to clipboard")
def passphrase(words, separator, capitalize, copy):
    """Generate a passphrase."""
    phrase = password_generator.generate_passphrase(
        word_count=words,
        separator=separator,
        capitalize=capitalize
    )
    
    if copy:
        try:
            pyperclip.copy(phrase)
            click.echo(f"{Fore.GREEN}Passphrase: {phrase} (copied to clipboard)")
        except Exception as e:
            click.echo(f"{Fore.YELLOW}Passphrase: {phrase} (clipboard copy failed: {e})")
    else:
        click.echo(f"Passphrase: {phrase}")


@cli.command()
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
def groups(database, password, keyfile):
    """List all groups in the database."""
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    groups = db_manager.get_groups()
    
    if not groups:
        click.echo("No groups found")
        return
    
    click.echo(f"\n{Fore.CYAN}Groups:")
    for group in groups:
        # Build path
        path_parts = []
        current = group
        while current:
            path_parts.insert(0, current.name)
            current = current.parentgroup if hasattr(current, 'parentgroup') else None
        
        path = "/".join(path_parts)
        click.echo(f"  {path}")


@cli.command("find-duplicates")
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.option("--output", "-o", type=click.Path(), help="Save report to file")
def find_duplicates(database, password, keyfile, json_output, output):
    """Find and report duplicate password entries.
    
    Scans the database for duplicate entries based on URL and username.
    Provides a comprehensive report of findings.
    """
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    click.echo(f"{Fore.CYAN}Scanning database for duplicates...")
    
    # Find duplicates
    finder = DuplicateFinder(db_manager.kp)
    report = finder.find_duplicates()
    
    # Generate output
    if json_output:
        # JSON output
        output_data = {
            "total_entries": report.total_entries,
            "duplicate_groups": len(report.duplicate_groups),
            "total_duplicates": report.total_duplicates,
            "redundant_entries": report.redundant_entries,
            "groups": []
        }
        
        for group in report.duplicate_groups:
            group_data = {
                "url": group.url,
                "username": group.username,
                "count": len(group.entries),
                "has_different_passwords": group.has_different_passwords,
                "entries": []
            }
            
            for entry in group.entries:
                entry_data = {
                    "title": entry.title,
                    "username": entry.username,
                    "url": entry.url,
                    "group": entry.group.name if entry.group else "",
                    "modified": entry.mtime.isoformat() if entry.mtime else None
                }
                group_data["entries"].append(entry_data)
            
            output_data["groups"].append(group_data)
        
        json_str = json.dumps(output_data, indent=2)
        
        if output:
            with open(output, 'w') as f:
                f.write(json_str)
            click.echo(f"{Fore.GREEN}Report saved to {output}")
        else:
            click.echo(json_str)
    else:
        # Human-readable output
        lines = []
        lines.append(f"\n{Fore.CYAN}{'='*80}")
        lines.append(f"{Fore.CYAN}Duplicate Entry Report")
        lines.append(f"{Fore.CYAN}{'='*80}\n")
        
        lines.append(f"{Fore.YELLOW}Statistics:")
        lines.append(f"  Total entries scanned:    {report.total_entries}")
        lines.append(f"  Duplicate groups found:   {len(report.duplicate_groups)}")
        lines.append(f"  Total duplicate entries:  {report.total_duplicates}")
        lines.append(f"  Redundant entries:        {report.redundant_entries}")
        lines.append("")
        
        if not report.has_duplicates():
            lines.append(f"{Fore.GREEN}✓ No duplicate entries found!")
        else:
            # Groups with different passwords (warnings)
            warning_groups = report.get_groups_with_different_passwords()
            if warning_groups:
                lines.append(f"{Fore.RED}⚠ Warning: {len(warning_groups)} group(s) have different passwords!")
                lines.append("")
            
            lines.append(f"{Fore.CYAN}Duplicate Groups:\n")
            
            for idx, group in enumerate(report.duplicate_groups, 1):
                lines.append(f"{Fore.CYAN}{'─'*80}")
                lines.append(f"{Fore.CYAN}Group {idx}: {group.url or '(no URL)'} - {group.username or '(no username)'}")
                
                if group.has_different_passwords:
                    lines.append(f"{Fore.RED}  ⚠ Entries have DIFFERENT passwords!")
                
                lines.append(f"  {Fore.YELLOW}Found {len(group.entries)} duplicate entries:")
                lines.append("")
                
                for entry_idx, entry in enumerate(group.entries, 1):
                    lines.append(f"  {entry_idx}. {Fore.WHITE}{entry.title}")
                    lines.append(f"     Username: {entry.username or '(none)'}")
                    lines.append(f"     URL:      {entry.url or '(none)'}")
                    lines.append(f"     Group:    {entry.group.name if entry.group else '(none)'}")
                    if entry.mtime:
                        lines.append(f"     Modified: {entry.mtime}")
                    if entry.notes:
                        notes_preview = entry.notes[:50] + "..." if len(entry.notes) > 50 else entry.notes
                        lines.append(f"     Notes:    {notes_preview}")
                    lines.append("")
        
        lines.append(f"{Fore.CYAN}{'='*80}\n")
        
        report_text = "\n".join(lines)
        
        if output:
            with open(output, 'w') as f:
                # Strip color codes for file output
                import re
                clean_text = re.sub(r'\x1b\[[0-9;]*m', '', report_text)
                f.write(clean_text)
            click.echo(f"{Fore.GREEN}Report saved to {output}")
        
        click.echo(report_text)


@cli.command("optimize")
@click.argument("database", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--dry-run", is_flag=True, help="Preview changes without modifying database")
def optimize(database, password, keyfile, dry_run):
    """Interactively optimize duplicate password entries.
    
    Presents duplicate entries and allows user to select which to keep,
    merge, or skip. Creates automatic backup before making changes.
    """
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    click.echo(f"{Fore.CYAN}Scanning database for duplicates...")
    
    # Find duplicates
    finder = DuplicateFinder(db_manager.kp)
    report = finder.find_duplicates()
    
    if not report.has_duplicates():
        click.echo(f"{Fore.GREEN}✓ No duplicate entries found! Database is already optimized.")
        return
    
    click.echo(f"\n{Fore.YELLOW}Found {len(report.duplicate_groups)} duplicate group(s) with {report.redundant_entries} redundant entries.")
    
    if dry_run:
        click.echo(f"\n{Fore.CYAN}DRY RUN MODE - No changes will be made\n")
    else:
        # Create backup
        backup_path = f"{database}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.kdbx"
        click.echo(f"\n{Fore.CYAN}Creating backup: {backup_path}")
        
        if not finder.create_backup(backup_path):
            click.echo(f"{Fore.RED}Failed to create backup. Aborting.")
            sys.exit(1)
        
        click.echo(f"{Fore.GREEN}✓ Backup created successfully")
    
    click.echo(f"\n{Fore.CYAN}{'='*80}")
    click.echo(f"{Fore.CYAN}Interactive Duplicate Optimization")
    click.echo(f"{Fore.CYAN}{'='*80}\n")
    
    entries_to_delete = []
    audit_log = []
    
    for idx, group in enumerate(report.duplicate_groups, 1):
        click.echo(f"\n{Fore.CYAN}{'─'*80}")
        click.echo(f"{Fore.CYAN}Group {idx} of {len(report.duplicate_groups)}")
        click.echo(f"{Fore.CYAN}URL: {group.url or '(no URL)'}")
        click.echo(f"{Fore.CYAN}Username: {group.username or '(no username)'}")
        
        if group.has_different_passwords:
            click.echo(f"{Fore.RED}⚠ WARNING: Entries have DIFFERENT passwords!")
        
        click.echo(f"\n{Fore.YELLOW}Duplicate entries:")
        
        for entry_idx, entry in enumerate(group.entries, 1):
            click.echo(f"\n  {Fore.WHITE}[{entry_idx}] {entry.title}")
            click.echo(f"      Username: {entry.username or '(none)'}")
            click.echo(f"      URL:      {entry.url or '(none)'}")
            click.echo(f"      Group:    {entry.group.name if entry.group else '(none)'}")
            if entry.mtime:
                click.echo(f"      Modified: {entry.mtime}")
            if entry.notes:
                notes_preview = entry.notes[:100] + "..." if len(entry.notes) > 100 else entry.notes
                click.echo(f"      Notes:    {notes_preview}")
        
        click.echo(f"\n{Fore.YELLOW}Options:")
        click.echo("  1-N : Keep entry N and mark others for deletion")
        click.echo("  s   : Skip this group (keep all duplicates)")
        click.echo("  q   : Quit optimization")
        
        while True:
            choice = click.prompt(f"\n{Fore.GREEN}Your choice", type=str).strip().lower()
            
            if choice == 'q':
                click.echo(f"\n{Fore.YELLOW}Optimization cancelled by user")
                return
            elif choice == 's':
                click.echo(f"{Fore.YELLOW}Skipping this group")
                audit_log.append(f"Skipped: {group.url} - {group.username}")
                break
            else:
                # Try to parse as entry number
                try:
                    entry_num = int(choice)
                    if 1 <= entry_num <= len(group.entries):
                        # Mark all other entries for deletion
                        kept_entry = group.entries[entry_num - 1]
                        click.echo(f"\n{Fore.GREEN}✓ Will keep: {kept_entry.title}")
                        
                        for i, entry in enumerate(group.entries):
                            if i != entry_num - 1:
                                entries_to_delete.append(entry)
                                click.echo(f"{Fore.RED}  ✗ Will delete: {entry.title}")
                        
                        audit_log.append(f"Kept '{kept_entry.title}', deleted {len(group.entries) - 1} duplicates for {group.url} - {group.username}")
                        break
                    else:
                        click.echo(f"{Fore.RED}Invalid choice. Please enter 1-{len(group.entries)}, 's', or 'q'")
                except ValueError:
                    click.echo(f"{Fore.RED}Invalid choice. Please enter 1-{len(group.entries)}, 's', or 'q'")
    
    # Summary
    click.echo(f"\n{Fore.CYAN}{'='*80}")
    click.echo(f"{Fore.CYAN}Optimization Summary")
    click.echo(f"{Fore.CYAN}{'='*80}\n")
    
    if not entries_to_delete:
        click.echo(f"{Fore.YELLOW}No entries marked for deletion")
        return
    
    click.echo(f"{Fore.YELLOW}Entries to delete: {len(entries_to_delete)}")
    for entry in entries_to_delete:
        click.echo(f"  • {entry.title}")
    
    if dry_run:
        click.echo(f"\n{Fore.CYAN}DRY RUN MODE - No changes were made")
        click.echo(f"{Fore.CYAN}Re-run without --dry-run to apply changes")
        return
    
    # Final confirmation
    click.echo(f"\n{Fore.RED}This will permanently delete {len(entries_to_delete)} entries!")
    if not click.confirm(f"{Fore.YELLOW}Are you sure you want to proceed?"):
        click.echo(f"\n{Fore.YELLOW}Optimization cancelled")
        return
    
    # Perform deletion
    click.echo(f"\n{Fore.CYAN}Deleting entries...")
    deleted_count = 0
    
    for entry in entries_to_delete:
        if db_manager.delete_entry(entry):
            deleted_count += 1
        else:
            click.echo(f"{Fore.RED}Failed to delete: {entry.title}")
    
    click.echo(f"\n{Fore.GREEN}✓ Successfully deleted {deleted_count} entries")
    click.echo(f"{Fore.GREEN}✓ Database optimized!")
    
    # Save audit log
    if audit_log:
        audit_file = f"{database}.audit.{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(audit_file, 'w') as f:
            f.write(f"Optimization performed on {datetime.now()}\n")
            f.write(f"Database: {database}\n")
            f.write(f"Backup: {backup_path}\n\n")
            f.write("Actions taken:\n")
            for log_entry in audit_log:
                f.write(f"  - {log_entry}\n")
            f.write(f"\nTotal entries deleted: {deleted_count}\n")
        
        click.echo(f"{Fore.CYAN}Audit log saved: {audit_file}")


@cli.command("export-csv")
@click.argument("database", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--include-passwords", is_flag=True, help="Include passwords in export (WARNING: CSV is not encrypted!)")
def export_csv(database, output, password, keyfile, include_passwords):
    """Export database entries to CSV file.
    
    WARNING: CSV files are not encrypted. Be careful when exporting passwords.
    """
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    if include_passwords:
        if not click.confirm(f"{Fore.YELLOW}WARNING: Passwords will be exported in plain text! Continue?"):
            click.echo("Export cancelled")
            return
    
    click.echo(f"{Fore.CYAN}Exporting database to CSV...")
    
    if db_manager.export_to_csv(output, include_passwords):
        click.echo(f"{Fore.GREEN}✓ Database exported successfully to {output}")
    else:
        click.echo(f"{Fore.RED}Failed to export database")
        sys.exit(1)


@cli.command("import-csv")
@click.argument("database", type=click.Path(exists=True))
@click.argument("input", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file path")
@click.option("--group", "-g", default="Imported", help="Default group for imported entries")
def import_csv(database, input, password, keyfile, group):
    """Import entries from CSV file.
    
    CSV should have columns: title, username, password, url, notes, tags, group
    """
    if not password:
        password = getpass("Enter master password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open database")
        sys.exit(1)
    
    click.echo(f"{Fore.CYAN}Importing entries from CSV...")
    
    results = db_manager.import_from_csv(input, group)
    
    if 'error' in results:
        click.echo(f"{Fore.RED}Error: {results['error']}")
        sys.exit(1)
    
    click.echo(f"\n{Fore.GREEN}Import completed:")
    click.echo(f"  Successfully imported: {results['success']}")
    click.echo(f"  Failed: {results['failed']}")
    click.echo(f"  Duplicates skipped: {len(results['duplicates'])}")
    
    if results['duplicates']:
        click.echo(f"\n{Fore.YELLOW}Duplicate entries (skipped):")
        for dup in results['duplicates'][:5]:
            click.echo(f"  - {dup['title']} ({dup['username']})")
        if len(results['duplicates']) > 5:
            click.echo(f"  ... and {len(results['duplicates']) - 5} more")
    
    if results.get('errors'):
        click.echo(f"\n{Fore.RED}Errors:")
        for error in results['errors'][:5]:
            click.echo(f"  - {error}")
        if len(results['errors']) > 5:
            click.echo(f"  ... and {len(results['errors']) - 5} more")


@cli.command("import-kdbx")
@click.argument("database", type=click.Path(exists=True))
@click.argument("source", type=click.Path(exists=True))
@click.option("--password", "-p", help="Master password for target database (will prompt if not provided)")
@click.option("--keyfile", "-k", type=click.Path(exists=True), help="Key file for target database")
@click.option("--source-password", "--sp", help="Password for source database (will prompt if not provided)")
@click.option("--source-keyfile", "--sk", type=click.Path(exists=True), help="Key file for source database")
def import_kdbx(database, source, password, keyfile, source_password, source_keyfile):
    """Import entries from another KDBX database.
    
    Merges entries from source database into target database.
    Duplicate entries (same title, username, URL) are skipped.
    """
    if not password:
        password = getpass("Enter target database password: ")
    
    if not source_password:
        source_password = getpass("Enter source database password: ")
    
    if not db_manager.open(database, password, keyfile):
        click.echo(f"{Fore.RED}Failed to open target database")
        sys.exit(1)
    
    click.echo(f"{Fore.CYAN}Importing entries from {source}...")
    
    results = db_manager.import_from_kdbx(source, source_password, source_keyfile)
    
    if 'error' in results:
        click.echo(f"{Fore.RED}Error: {results['error']}")
        sys.exit(1)
    
    click.echo(f"\n{Fore.GREEN}Import completed:")
    click.echo(f"  Successfully imported: {results['success']}")
    click.echo(f"  Failed: {results['failed']}")
    click.echo(f"  Duplicates found: {len(results['duplicates'])}")
    
    if results['duplicates']:
        click.echo(f"\n{Fore.YELLOW}Duplicate entries (skipped):")
        for dup in results['duplicates'][:5]:
            click.echo(f"  - {dup['title']} ({dup['username']}) - {dup['url']}")
        if len(results['duplicates']) > 5:
            click.echo(f"  ... and {len(results['duplicates']) - 5} more")
    
    if results.get('errors'):
        click.echo(f"\n{Fore.RED}Errors:")
        for error in results['errors'][:5]:
            click.echo(f"  - {error}")
        if len(results['errors']) > 5:
            click.echo(f"  ... and {len(results['errors']) - 5} more")


if __name__ == "__main__":
    cli()
