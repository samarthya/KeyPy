"""Database operations module."""
from pykeepass import PyKeePass, create_database
from pykeepass.exceptions import CredentialsError
import os
import csv
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime


class DatabaseManager:
    """Manages KeePass database operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.kp: Optional[PyKeePass] = None
        self.filepath: Optional[Path] = None
        self.modified: bool = False
        
    def create(self, filepath: str, password: str, keyfile: Optional[str] = None) -> bool:
        """
        Create a new KeePass database.
        
        Args:
            filepath: Path to the new database file
            password: Master password
            keyfile: Optional keyfile path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.kp = create_database(filepath, password=password, keyfile=keyfile)
            self.filepath = Path(filepath)
            self.kp.save()
            return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    
    def open(self, filepath: str, password: str, keyfile: Optional[str] = None) -> bool:
        """
        Open an existing KeePass database.
        
        Args:
            filepath: Path to the database file
            password: Master password
            keyfile: Optional keyfile path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                print(f"Database file not found: {filepath}")
                return False
            
            self.kp = PyKeePass(filepath, password=password, keyfile=keyfile)
            self.filepath = Path(filepath)
            return True
        except CredentialsError:
            print("Invalid credentials")
            return False
        except Exception as e:
            print(f"Error opening database: {e}")
            return False
    
    def save(self) -> bool:
        """Save the current database."""
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            self.kp.save()
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def close(self):
        """Close the current database."""
        self.kp = None
        self.filepath = None
    
    def is_open(self) -> bool:
        """Check if a database is currently open."""
        return self.kp is not None
    
    def add_entry(self, group_path: str, title: str, username: str, 
                  password: str, url: Optional[str] = None, 
                  notes: Optional[str] = None, tags: Optional[str] = None,
                  icon: Optional[str] = None) -> bool:
        """
        Add a new entry to the database.
        
        Args:
            group_path: Path to the group (e.g., "Root/Internet")
            title: Entry title
            username: Username
            password: Password
            url: Optional URL
            notes: Optional notes
            tags: Optional tags (comma-separated)
            icon: Optional icon name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            # Get or create group
            group = self._get_or_create_group(group_path)
            
            # Add entry
            entry = self.kp.add_entry(
                destination_group=group,
                title=title,
                username=username,
                password=password,
                url=url or "",
                notes=notes or ""
            )
            
            # Set tags if provided
            if tags:
                entry.tags = tags
            
            # Set icon if provided
            if icon:
                entry.icon = icon
                
            self.kp.save()
            self.modified = False
            return True
        except Exception as e:
            print(f"Error adding entry: {e}")
            return False
    
    def get_entries(self, search: Optional[str] = None) -> List:
        """
        Get entries from the database.
        
        Args:
            search: Optional search term (searches title, username, url, tags)
            
        Returns:
            List of entries
        """
        if not self.kp:
            return []
        
        try:
            if search:
                # Search in multiple fields including tags
                results = []
                search_lower = search.lower()
                for entry in self.kp.entries:
                    # Check title, username, url, and tags
                    # Handle tags which might be a list or string
                    tags_str = ""
                    if entry.tags:
                        if isinstance(entry.tags, list):
                            tags_str = ",".join(entry.tags).lower()
                        else:
                            tags_str = str(entry.tags).lower()
                    
                    if (entry.title and search_lower in entry.title.lower()) or \
                       (entry.username and search_lower in entry.username.lower()) or \
                       (entry.url and search_lower in entry.url.lower()) or \
                       (tags_str and search_lower in tags_str):
                        results.append(entry)
                return results
            else:
                return self.kp.entries
        except Exception as e:
            print(f"Error getting entries: {e}")
            return []
    
    def find_entries(self, **kwargs) -> List:
        """
        Find entries by various criteria.
        
        Args:
            **kwargs: Search criteria (title, username, url, etc.)
            
        Returns:
            List of matching entries
        """
        if not self.kp:
            return []
        
        try:
            return self.kp.find_entries(**kwargs)
        except Exception as e:
            print(f"Error finding entries: {e}")
            return []
    
    def delete_entry(self, entry, use_recycle_bin: bool = True) -> bool:
        """
        Delete an entry from the database.
        
        Args:
            entry: Entry object to delete
            use_recycle_bin: If True, move to recycle bin instead of permanent deletion
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            if use_recycle_bin:
                # Use PyKeePass's trash_entry method
                self.kp.trash_entry(entry)
            else:
                # Permanent deletion
                self.kp.delete_entry(entry)
            self.kp.save()
            self.modified = False
            return True
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
    
    def update_entry(self, entry, **kwargs) -> bool:
        """
        Update an entry in the database.
        
        Args:
            entry: Entry object to update
            **kwargs: Fields to update (title, username, password, url, notes, tags, icon)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            for key, value in kwargs.items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
            
            self.modified = True
            return True
        except Exception as e:
            print(f"Error updating entry: {e}")
            return False
    
    def save_if_modified(self) -> bool:
        """
        Save database if it has been modified.
        
        Returns:
            True if saved or not needed, False on error
        """
        if self.modified:
            return self.save()
        return True
    
    def add_group(self, group_path: str) -> bool:
        """
        Add a new group to the database.
        
        Args:
            group_path: Path to the group (e.g., "Root/Internet/Social")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            self._get_or_create_group(group_path)
            self.kp.save()
            return True
        except Exception as e:
            print(f"Error adding group: {e}")
            return False
    
    def _get_or_create_group(self, group_path: str):
        """
        Get or create a group by path.
        
        Args:
            group_path: Path to the group
            
        Returns:
            Group object
        """
        parts = [p for p in group_path.split("/") if p]
        
        if not parts:
            return self.kp.root_group
        
        current_group = self.kp.root_group
        
        for part in parts:
            # Try to find existing subgroup
            subgroup = self.kp.find_groups(name=part, group=current_group, first=True)
            
            if subgroup:
                current_group = subgroup
            else:
                # Create new subgroup
                current_group = self.kp.add_group(current_group, part)
        
        return current_group
    
    def get_groups(self) -> List:
        """
        Get all groups from the database.
        
        Returns:
            List of groups
        """
        if not self.kp:
            return []
        
        return self.kp.groups
    
    def export_to_csv(self, filepath: str, include_passwords: bool = True) -> bool:
        """
        Export database entries to CSV file.
        
        Args:
            filepath: Path to CSV file
            include_passwords: Whether to include passwords in export
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['title', 'username', 'url', 'notes', 'tags', 'group']
                if include_passwords:
                    fieldnames.insert(2, 'password')
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in self.kp.entries:
                    # Convert tags list to comma-separated string
                    tags_str = ''
                    if entry.tags:
                        if isinstance(entry.tags, list):
                            tags_str = ','.join(entry.tags)
                        else:
                            tags_str = str(entry.tags)
                    
                    row = {
                        'title': entry.title or '',
                        'username': entry.username or '',
                        'url': entry.url or '',
                        'notes': entry.notes or '',
                        'tags': tags_str,
                        'group': entry.group.name if entry.group else ''
                    }
                    if include_passwords:
                        row['password'] = entry.password or ''
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def import_from_csv(self, filepath: str, default_group: str = "Imported") -> Dict[str, Any]:
        """
        Import entries from CSV file.
        
        Args:
            filepath: Path to CSV file
            default_group: Default group for imported entries
            
        Returns:
            Dictionary with import results (success, failed, duplicates)
        """
        if not self.kp:
            return {'success': 0, 'failed': 0, 'error': 'No database loaded'}
        
        results = {'success': 0, 'failed': 0, 'duplicates': [], 'errors': []}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        title = row.get('title', 'Untitled')
                        username = row.get('username', '')
                        password = row.get('password', '')
                        url = row.get('url', '')
                        notes = row.get('notes', '')
                        tags = row.get('tags', '')
                        group = row.get('group', default_group)
                        
                        # Check for duplicates
                        existing = self.find_entries(title=title, username=username, url=url, first=True)
                        if existing:
                            results['duplicates'].append({
                                'title': title,
                                'username': username,
                                'url': url
                            })
                            continue
                        
                        # Add entry
                        if self.add_entry(group, title, username, password, url, notes, tags):
                            results['success'] += 1
                        else:
                            results['failed'] += 1
                            results['errors'].append(f"Failed to add: {title}")
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Error importing row: {e}")
            
            return results
        except Exception as e:
            return {'success': 0, 'failed': 0, 'error': f"Error reading CSV: {e}"}
    
    def import_from_kdbx(self, source_filepath: str, source_password: str, 
                        source_keyfile: Optional[str] = None) -> Dict[str, Any]:
        """
        Import entries from another KDBX database.
        
        Args:
            source_filepath: Path to source database
            source_password: Password for source database
            source_keyfile: Optional keyfile for source database
            
        Returns:
            Dictionary with import results
        """
        if not self.kp:
            return {'success': 0, 'failed': 0, 'error': 'No database loaded'}
        
        results = {'success': 0, 'failed': 0, 'duplicates': [], 'errors': []}
        
        try:
            # Open source database
            source_kp = PyKeePass(source_filepath, password=source_password, keyfile=source_keyfile)
            
            for entry in source_kp.entries:
                try:
                    # Check for duplicates based on title, username, and url
                    existing = None
                    if entry.url and entry.username:
                        existing = self.find_entries(
                            title=entry.title,
                            username=entry.username,
                            url=entry.url,
                            first=True
                        )
                    
                    if existing:
                        results['duplicates'].append({
                            'title': entry.title,
                            'username': entry.username,
                            'url': entry.url,
                            'entry': entry
                        })
                    else:
                        # Import the entry
                        group_path = entry.group.name if entry.group else "Imported"
                        if self.add_entry(
                            group_path,
                            entry.title or 'Untitled',
                            entry.username or '',
                            entry.password or '',
                            entry.url or '',
                            entry.notes or '',
                            entry.tags or ''
                        ):
                            results['success'] += 1
                        else:
                            results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error importing entry: {e}")
            
            return results
        except CredentialsError:
            return {'success': 0, 'failed': 0, 'error': 'Invalid credentials for source database'}
        except Exception as e:
            return {'success': 0, 'failed': 0, 'error': f"Error opening source database: {e}"}
