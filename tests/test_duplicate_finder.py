"""Tests for duplicate finder module."""
import pytest
import tempfile
import os
from datetime import datetime

from keypy.core.database import DatabaseManager
from keypy.core.duplicate_finder import DuplicateFinder, DuplicateReport, DuplicateGroup


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.kdbx', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_with_duplicates(temp_db):
    """Create a database with duplicate entries."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add duplicate entries with same URL and username
    manager.add_entry("Root", "GitHub - Main", "user@example.com", "pass1", "https://github.com")
    manager.add_entry("Root", "GitHub - Work", "user@example.com", "pass1", "https://github.com")
    
    # Add duplicates with www variant
    manager.add_entry("Root", "Facebook 1", "john@example.com", "pass2", "https://www.facebook.com")
    manager.add_entry("Root", "Facebook 2", "john@example.com", "pass2", "https://facebook.com")
    
    # Add duplicates with different passwords (should be warned)
    manager.add_entry("Root", "Twitter Old", "user@example.com", "oldpass", "https://twitter.com")
    manager.add_entry("Root", "Twitter New", "user@example.com", "newpass", "https://twitter.com")
    
    # Add unique entry (not a duplicate)
    manager.add_entry("Root", "LinkedIn", "unique@example.com", "pass3", "https://linkedin.com")
    
    # Add duplicates with case variations
    manager.add_entry("Root", "Gmail 1", "User@Gmail.com", "pass4", "https://gmail.com")
    manager.add_entry("Root", "Gmail 2", "user@gmail.com", "pass4", "https://Gmail.com")
    
    return manager


@pytest.fixture
def empty_db(temp_db):
    """Create an empty database."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    return manager


@pytest.fixture
def db_no_duplicates(temp_db):
    """Create a database with no duplicates."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    manager.add_entry("Root", "Entry1", "user1@example.com", "pass1", "https://site1.com")
    manager.add_entry("Root", "Entry2", "user2@example.com", "pass2", "https://site2.com")
    manager.add_entry("Root", "Entry3", "user3@example.com", "pass3", "https://site3.com")
    
    return manager


def test_normalize_url():
    """Test URL normalization."""
    # Test www removal
    assert DuplicateFinder.normalize_url("https://www.example.com") == "https://example.com"
    assert DuplicateFinder.normalize_url("https://example.com") == "https://example.com"
    
    # Test case insensitivity
    assert DuplicateFinder.normalize_url("HTTPS://Example.COM") == "https://example.com"
    
    # Test scheme addition
    assert DuplicateFinder.normalize_url("example.com") == "https://example.com"
    
    # Test trailing slash removal
    assert DuplicateFinder.normalize_url("https://example.com/") == "https://example.com"
    assert DuplicateFinder.normalize_url("https://example.com/path/") == "https://example.com/path"
    
    # Test empty/None
    assert DuplicateFinder.normalize_url("") == ""
    assert DuplicateFinder.normalize_url(None) == ""
    assert DuplicateFinder.normalize_url("   ") == ""


def test_normalize_username():
    """Test username normalization."""
    # Test case insensitivity
    assert DuplicateFinder.normalize_username("User@Example.com") == "user@example.com"
    assert DuplicateFinder.normalize_username("USER@EXAMPLE.COM") == "user@example.com"
    
    # Test whitespace trimming
    assert DuplicateFinder.normalize_username("  user@example.com  ") == "user@example.com"
    
    # Test empty/None
    assert DuplicateFinder.normalize_username("") == ""
    assert DuplicateFinder.normalize_username(None) == ""


def test_find_duplicates_in_db_with_duplicates(db_with_duplicates):
    """Test finding duplicates in a database with duplicates."""
    finder = DuplicateFinder(db_with_duplicates.kp)
    report = finder.find_duplicates()
    
    # Check report structure
    assert isinstance(report, DuplicateReport)
    assert report.total_entries >= 8  # At least 8 entries added (may have default entry)
    assert report.has_duplicates()
    
    # Should find 4 duplicate groups (GitHub, Facebook, Twitter, Gmail)
    assert len(report.duplicate_groups) == 4
    
    # Check each group has 2 entries
    for group in report.duplicate_groups:
        assert len(group.entries) == 2
    
    # Total duplicates = 8 entries (4 groups × 2 entries)
    assert report.total_duplicates == 8
    
    # Redundant entries = 4 (one per group could be eliminated)
    assert report.redundant_entries == 4


def test_find_duplicates_empty_db(empty_db):
    """Test finding duplicates in an empty database."""
    finder = DuplicateFinder(empty_db.kp)
    report = finder.find_duplicates()
    
    assert report.total_entries == 0
    assert not report.has_duplicates()
    assert len(report.duplicate_groups) == 0
    assert report.total_duplicates == 0
    assert report.redundant_entries == 0


def test_find_duplicates_no_duplicates(db_no_duplicates):
    """Test finding duplicates when there are none."""
    finder = DuplicateFinder(db_no_duplicates.kp)
    report = finder.find_duplicates()
    
    assert report.total_entries == 3
    assert not report.has_duplicates()
    assert len(report.duplicate_groups) == 0
    assert report.total_duplicates == 0
    assert report.redundant_entries == 0


def test_duplicate_group_with_different_passwords(db_with_duplicates):
    """Test detection of groups with different passwords."""
    finder = DuplicateFinder(db_with_duplicates.kp)
    report = finder.find_duplicates()
    
    # Get groups with different passwords
    different_pass_groups = report.get_groups_with_different_passwords()
    
    # Only Twitter group has different passwords
    assert len(different_pass_groups) == 1
    
    twitter_group = different_pass_groups[0]
    assert twitter_group.has_different_passwords
    assert "twitter.com" in twitter_group.url


def test_duplicate_group_methods(db_with_duplicates):
    """Test DuplicateGroup helper methods."""
    finder = DuplicateFinder(db_with_duplicates.kp)
    report = finder.find_duplicates()
    
    # Get first group
    group = report.duplicate_groups[0]
    
    # Test entry retrieval
    newest = group.get_newest_entry()
    oldest = group.get_oldest_entry()
    
    assert newest is not None
    assert oldest is not None
    assert newest in group.entries
    assert oldest in group.entries


def test_url_normalization_with_paths():
    """Test URL normalization with paths."""
    url1 = "https://example.com/login"
    url2 = "https://www.example.com/login"
    
    norm1 = DuplicateFinder.normalize_url(url1)
    norm2 = DuplicateFinder.normalize_url(url2)
    
    assert norm1 == norm2
    assert norm1 == "https://example.com/login"


def test_create_backup(db_with_duplicates, tmp_path):
    """Test creating database backup."""
    finder = DuplicateFinder(db_with_duplicates.kp)
    backup_path = tmp_path / "backup.kdbx"
    
    result = finder.create_backup(str(backup_path))
    
    assert result is True
    assert backup_path.exists()
    
    # Verify backup can be opened
    from keypy.core.database import DatabaseManager
    backup_manager = DatabaseManager()
    assert backup_manager.open(str(backup_path), "test_password")


def test_all_duplicates_scenario(temp_db):
    """Test database where all entries are duplicates."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add 5 entries all with same URL and username
    for i in range(5):
        manager.add_entry("Root", f"Entry {i}", "user@example.com", f"pass{i}", "https://example.com")
    
    finder = DuplicateFinder(manager.kp)
    report = finder.find_duplicates()
    
    assert report.total_entries == 5
    assert report.has_duplicates()
    assert len(report.duplicate_groups) == 1
    assert len(report.duplicate_groups[0].entries) == 5
    assert report.total_duplicates == 5
    assert report.redundant_entries == 4


def test_case_insensitive_username_matching(temp_db):
    """Test that username matching is case-insensitive."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add entries with different case usernames
    manager.add_entry("Root", "Entry1", "User@Example.COM", "pass1", "https://example.com")
    manager.add_entry("Root", "Entry2", "user@example.com", "pass1", "https://example.com")
    manager.add_entry("Root", "Entry3", "USER@EXAMPLE.COM", "pass1", "https://example.com")
    
    finder = DuplicateFinder(manager.kp)
    report = finder.find_duplicates()
    
    # Should find 1 group with 3 entries (all same user, different case)
    assert len(report.duplicate_groups) == 1
    assert len(report.duplicate_groups[0].entries) == 3
