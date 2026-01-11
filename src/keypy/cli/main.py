"""Command-line interface for KeyPy."""
import click
import sys
import os
from pathlib import Path
from getpass import getpass
import pyperclip
from colorama import init, Fore, Style

from keypy.core.database import DatabaseManager
from keypy.core.password_generator import PasswordGenerator

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
@click.option("--generate", is_flag=True, help="Generate password")
@click.option("--length", "-l", default=16, help="Generated password length")
def add(database, password, keyfile, group, title, username, password_value, url, notes, generate, length):
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
    
    if db_manager.add_entry(group, title, username, password_value, url, notes):
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


if __name__ == "__main__":
    cli()
