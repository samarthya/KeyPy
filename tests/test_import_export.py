"""Tests for import/export functionality."""
import pytest
import tempfile
import os
import csv
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


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
    yield csv_path
    # Cleanup
    if os.path.exists(csv_path):
        os.remove(csv_path)


def test_export_to_csv_with_passwords(temp_db, temp_csv):
    """Test exporting database to CSV with passwords."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add entries with tags
    manager.add_entry(
        "Root", "GitHub", "user1", "pass1",
        "https://github.com", "Notes 1",
        tags="work,dev"
    )
    manager.add_entry(
        "Root", "GitLab", "user2", "pass2",
        "https://gitlab.com", "Notes 2",
        tags="work"
    )
    
    # Export to CSV
    result = manager.export_to_csv(temp_csv, include_passwords=True)
    assert result is True
    
    # Verify CSV content
    with open(temp_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]['title'] == 'GitHub'
        assert rows[0]['password'] == 'pass1'
        assert rows[0]['tags'] == 'work,dev'
        assert rows[1]['title'] == 'GitLab'
        assert rows[1]['password'] == 'pass2'
        assert rows[1]['tags'] == 'work'


def test_export_to_csv_without_passwords(temp_db, temp_csv):
    """Test exporting database to CSV without passwords."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    manager.add_entry("Root", "Test", "user", "pass", "https://test.com")
    
    # Export without passwords
    result = manager.export_to_csv(temp_csv, include_passwords=False)
    assert result is True
    
    # Verify CSV doesn't have password field
    with open(temp_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        assert len(rows) == 1
        assert 'password' not in rows[0]
        assert rows[0]['title'] == 'Test'
        assert rows[0]['username'] == 'user'


def test_import_from_csv(temp_db, temp_csv):
    """Test importing entries from CSV."""
    # Create CSV file
    with open(temp_csv, 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['title', 'username', 'password', 'url', 'notes', 'tags', 'group']
        )
        writer.writeheader()
        writer.writerow({
            'title': 'Test1',
            'username': 'user1',
            'password': 'pass1',
            'url': 'https://test1.com',
            'notes': 'Notes 1',
            'tags': 'tag1,tag2',
            'group': 'Internet'
        })
        writer.writerow({
            'title': 'Test2',
            'username': 'user2',
            'password': 'pass2',
            'url': 'https://test2.com',
            'notes': 'Notes 2',
            'tags': 'tag3',
            'group': 'Work'
        })
    
    # Import into database
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    results = manager.import_from_csv(temp_csv)
    
    assert results['success'] == 2
    assert results['failed'] == 0
    assert len(results['duplicates']) == 0
    
    # Verify entries
    entries = manager.get_entries()
    assert len(entries) == 2


def test_import_from_csv_skip_duplicates(temp_db, temp_csv):
    """Test that duplicate entries are skipped during import."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add an entry
    manager.add_entry(
        "Root", "Existing", "user", "pass",
        "https://existing.com"
    )
    
    # Create CSV with same entry
    with open(temp_csv, 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['title', 'username', 'password', 'url', 'notes', 'tags', 'group']
        )
        writer.writeheader()
        writer.writerow({
            'title': 'Existing',
            'username': 'user',
            'password': 'pass',
            'url': 'https://existing.com',
            'notes': '',
            'tags': '',
            'group': 'Root'
        })
        writer.writerow({
            'title': 'New Entry',
            'username': 'newuser',
            'password': 'newpass',
            'url': 'https://new.com',
            'notes': '',
            'tags': '',
            'group': 'Root'
        })
    
    results = manager.import_from_csv(temp_csv)
    
    # One should be skipped as duplicate, one should succeed
    assert results['success'] == 1
    assert len(results['duplicates']) == 1
    
    # Should have 2 entries total (1 original + 1 new)
    entries = manager.get_entries()
    assert len(entries) == 2


def test_import_from_kdbx(temp_db):
    """Test importing from another KDBX database."""
    # Create source database
    source_db = tempfile.NamedTemporaryFile(delete=False, suffix='.kdbx')
    source_path = source_db.name
    source_db.close()
    
    try:
        source_manager = DatabaseManager()
        source_manager.create(source_path, password="source_pass")
        source_manager.add_entry(
            "Root", "Source Entry", "source_user", "source_pass",
            "https://source.com", "Source notes",
            tags="imported"
        )
        
        # Create target database
        target_manager = DatabaseManager()
        target_manager.create(temp_db, password="target_pass")
        
        # Import from source
        results = target_manager.import_from_kdbx(source_path, "source_pass")
        
        assert results['success'] == 1
        assert results['failed'] == 0
        
        # Verify entry was imported
        entries = target_manager.get_entries()
        assert len(entries) == 1
        assert entries[0].title == 'Source Entry'
        
    finally:
        if os.path.exists(source_path):
            os.remove(source_path)


def test_tags_and_icons(temp_db):
    """Test adding entries with tags and icons."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add entry with tags and icon
    result = manager.add_entry(
        "Root", "Tagged Entry", "user", "pass",
        "https://example.com", "Test notes",
        tags="work,important,dev",
        icon="1"
    )
    
    assert result is True
    
    # Verify tags
    entries = manager.get_entries()
    assert len(entries) == 1
    assert entries[0].tags == ['work', 'important', 'dev']
    assert entries[0].icon == '1'


def test_search_by_tags(temp_db):
    """Test searching entries by tags."""
    manager = DatabaseManager()
    manager.create(temp_db, password="test_password")
    
    # Add entries with different tags
    manager.add_entry(
        "Root", "Work Item", "user1", "pass1",
        tags="work,urgent"
    )
    manager.add_entry(
        "Root", "Personal Item", "user2", "pass2",
        tags="personal,hobby"
    )
    manager.add_entry(
        "Root", "Mixed Item", "user3", "pass3",
        tags="work,personal"
    )
    
    # Search for 'work' tag
    results = manager.get_entries(search="work")
    assert len(results) == 2  # Should find "Work Item" and "Mixed Item"
    
    # Search for 'personal' tag
    results = manager.get_entries(search="personal")
    assert len(results) == 2  # Should find "Personal Item" and "Mixed Item"
    
    # Search for 'urgent' tag
    results = manager.get_entries(search="urgent")
    assert len(results) == 1  # Should find only "Work Item"
