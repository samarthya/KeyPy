"""Database operations module."""
from pykeepass import PyKeePass, create_database
from pykeepass.exceptions import CredentialsError
import os
from typing import Optional, List
from pathlib import Path


class DatabaseManager:
    """Manages KeePass database operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.kp: Optional[PyKeePass] = None
        self.filepath: Optional[Path] = None
        
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
                  notes: Optional[str] = None) -> bool:
        """
        Add a new entry to the database.
        
        Args:
            group_path: Path to the group (e.g., "Root/Internet")
            title: Entry title
            username: Username
            password: Password
            url: Optional URL
            notes: Optional notes
            
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
            self.kp.add_entry(
                destination_group=group,
                title=title,
                username=username,
                password=password,
                url=url or "",
                notes=notes or ""
            )
            self.kp.save()
            return True
        except Exception as e:
            print(f"Error adding entry: {e}")
            return False
    
    def get_entries(self, search: Optional[str] = None) -> List:
        """
        Get entries from the database.
        
        Args:
            search: Optional search term
            
        Returns:
            List of entries
        """
        if not self.kp:
            return []
        
        try:
            if search:
                return self.kp.find_entries(title=search, regex=True, flags="i")
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
    
    def delete_entry(self, entry) -> bool:
        """
        Delete an entry from the database.
        
        Args:
            entry: Entry object to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kp:
            print("No database loaded")
            return False
        
        try:
            self.kp.delete_entry(entry)
            self.kp.save()
            return True
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
    
    def update_entry(self, entry, **kwargs) -> bool:
        """
        Update an entry in the database.
        
        Args:
            entry: Entry object to update
            **kwargs: Fields to update (title, username, password, url, notes)
            
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
            
            self.kp.save()
            return True
        except Exception as e:
            print(f"Error updating entry: {e}")
            return False
    
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
