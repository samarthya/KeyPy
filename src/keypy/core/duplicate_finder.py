"""Duplicate password finder and optimizer module."""
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime
import shutil


class DuplicateGroup:
    """Represents a group of duplicate entries."""
    
    def __init__(self, url: str, username: str, entries: List):
        """
        Initialize a duplicate group.
        
        Args:
            url: Normalized URL
            username: Normalized username
            entries: List of duplicate entries
        """
        self.url = url
        self.username = username
        self.entries = entries
        self.has_different_passwords = self._check_different_passwords()
    
    def _check_different_passwords(self) -> bool:
        """Check if entries have different passwords."""
        if len(self.entries) <= 1:
            return False
        passwords = set(entry.password for entry in self.entries)
        return len(passwords) > 1
    
    def get_newest_entry(self):
        """Get the most recently modified entry."""
        return max(self.entries, key=lambda e: e.mtime if e.mtime else datetime.min)
    
    def get_oldest_entry(self):
        """Get the oldest entry."""
        return min(self.entries, key=lambda e: e.ctime if e.ctime else datetime.max)


class DuplicateReport:
    """Report of duplicate entries found in database."""
    
    def __init__(self, total_entries: int, duplicate_groups: List[DuplicateGroup]):
        """
        Initialize duplicate report.
        
        Args:
            total_entries: Total number of entries scanned
            duplicate_groups: List of duplicate groups found
        """
        self.total_entries = total_entries
        self.duplicate_groups = duplicate_groups
        self.total_duplicates = sum(len(group.entries) for group in duplicate_groups)
        self.redundant_entries = self.total_duplicates - len(duplicate_groups)
    
    def has_duplicates(self) -> bool:
        """Check if any duplicates were found."""
        return len(self.duplicate_groups) > 0
    
    def get_groups_with_different_passwords(self) -> List[DuplicateGroup]:
        """Get duplicate groups where entries have different passwords."""
        return [group for group in self.duplicate_groups if group.has_different_passwords]


class DuplicateFinder:
    """Find and analyze duplicate entries in KeePass database."""
    
    def __init__(self, kp):
        """
        Initialize duplicate finder.
        
        Args:
            kp: PyKeePass database instance
        """
        self.kp = kp
    
    @staticmethod
    def normalize_url(url: Optional[str]) -> str:
        """
        Normalize URL for comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL string
        """
        if not url or url.strip() == "":
            return ""
        
        url = url.lower().strip()
        
        # Parse URL
        try:
            parsed = urlparse(url)
            
            # If no scheme, add https://
            if not parsed.scheme:
                url = "https://" + url
                parsed = urlparse(url)
            
            # Normalize domain: remove www. prefix
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Reconstruct normalized URL (scheme + domain + path)
            path = parsed.path.rstrip("/") if parsed.path != "/" else ""
            normalized = f"{parsed.scheme}://{domain}{path}"
            
            return normalized
        except Exception:
            # If parsing fails, return lowercase original
            return url.lower()
    
    @staticmethod
    def normalize_username(username: Optional[str]) -> str:
        """
        Normalize username for comparison.
        
        Args:
            username: Username to normalize
            
        Returns:
            Normalized username string
        """
        if not username:
            return ""
        return username.lower().strip()
    
    def find_duplicates(self) -> DuplicateReport:
        """
        Find duplicate entries in the database.
        
        Returns:
            DuplicateReport with findings
        """
        entries = self.kp.entries
        total_entries = len(entries)
        
        # Group entries by normalized URL and username
        groups_dict = defaultdict(list)
        
        for entry in entries:
            normalized_url = self.normalize_url(entry.url)
            normalized_username = self.normalize_username(entry.username)
            
            # Create a key from normalized URL and username
            key = (normalized_url, normalized_username)
            groups_dict[key].append(entry)
        
        # Filter to only groups with duplicates (more than 1 entry)
        duplicate_groups = []
        for (url, username), entries_list in groups_dict.items():
            if len(entries_list) > 1:
                duplicate_groups.append(DuplicateGroup(url, username, entries_list))
        
        # Sort by number of duplicates (descending)
        duplicate_groups.sort(key=lambda g: len(g.entries), reverse=True)
        
        return DuplicateReport(total_entries, duplicate_groups)
    
    def create_backup(self, backup_path: str) -> bool:
        """
        Create a backup of the current database.
        
        Args:
            backup_path: Path to save backup
            
        Returns:
            True if successful, False otherwise
        """
        try:
            shutil.copy2(self.kp.filename, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
