"""Tests for database operations."""
import pytest
import tempfile
import os
from pathlib import Path

from keypy.core.database import DatabaseManager


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.kdbx', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


def test_create_database(temp_db):
    """Test database creation."""
    manager = DatabaseManager()
    result = manager.create(temp_db, password="test_password")
    
    assert result is True
    assert os.path.exists(temp_db)
    assert manager.is_open()


def test_open_database(temp_db):
    """Test opening an existing database."""
    # First create a database
    manager1 = DatabaseManager()
    manager1.create(temp_db, password="test_password")
    manager1.close()
    
    # Now open it
    manager2 = DatabaseManager()
    result = manager2.open(temp_db, password="test_password")
    
    assert result is True
    assert manager2.is_open()


def test_open_database_wrong_password(temp_db):
    """Test opening database with wrong password."""
    # Create database
    manager1 = DatabaseManager()
    manager1.create(temp_db, password="test_password")
    manager1.close()
    
    # Try to open with wrong password
    manager2 = DatabaseManager()
    result = manager2.open(temp_db, password="wrong_password")
    
    assert result is False
    assert not manager2.is_open()


def test_add_entry(temp_db):
    """Test adding an entry."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    result = manager.add_entry(
        group_path="Root",
        title="Test Entry",
        username="testuser",
        password="testpass",
        url="https://example.com",
        notes="Test notes"
    )
    
    assert result is True
    
    # Verify entry exists
    entries = manager.get_entries()
    assert len(entries) == 1
    assert entries[0].title == "Test Entry"
    assert entries[0].username == "testuser"


def test_delete_entry(temp_db):
    """Test deleting an entry."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add entry
    manager.add_entry(
        group_path="Root",
        title="Test Entry",
        username="testuser",
        password="testpass"
    )
    
    # Get the entry
    entries = manager.get_entries()
    assert len(entries) == 1
    
    # Delete it
    result = manager.delete_entry(entries[0])
    assert result is True
    
    # Verify it's gone
    entries = manager.get_entries()
    assert len(entries) == 0


def test_find_entries(temp_db):
    """Test finding entries."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add multiple entries
    manager.add_entry("Root", "GitHub", "user1", "pass1")
    manager.add_entry("Root", "GitLab", "user2", "pass2")
    manager.add_entry("Root", "Email", "user3", "pass3")
    
    # Find by title
    entries = manager.find_entries(title="GitHub", regex=False)
    assert len(entries) == 1
    assert entries[0].title == "GitHub"


def test_add_group(temp_db):
    """Test adding a group."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    result = manager.add_group("Root/Internet/Social")
    assert result is True
    
    groups = manager.get_groups()
    assert len(groups) > 1  # Root + created groups
