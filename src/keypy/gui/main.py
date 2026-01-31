"""Main GUI application for KeyPy."""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QMessageBox, QInputDialog,
    QFileDialog, QDialog, QFormLayout, QTextEdit, QMenuBar,
    QMenu, QToolBar, QStatusBar, QSplitter, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QFont

from keypy.core.database import DatabaseManager
from keypy.core.password_generator import PasswordGenerator


class KeyPyMainWindow(QMainWindow):
    """Main window for KeyPy GUI."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.db_manager = DatabaseManager()
        self.password_generator = PasswordGenerator()
        
        self.setWindowTitle("KeyPy - Password Manager")
        self.setGeometry(100, 100, 1200, 700)
        
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Group tree
        self.group_tree = QTreeWidget()
        self.group_tree.setHeaderLabel("Groups")
        self.group_tree.setMinimumWidth(200)
        self.group_tree.itemClicked.connect(self._on_group_selected)
        splitter.addWidget(self.group_tree)
        
        # Right panel - Entry table
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        right_layout.addLayout(search_layout)
        
        # Entry table
        self.entry_table = QTableWidget()
        self.entry_table.setColumnCount(5)
        self.entry_table.setHorizontalHeaderLabels(["Title", "Username", "URL", "Tags", "Modified"])
        self.entry_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.entry_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.entry_table.doubleClicked.connect(self._on_entry_double_clicked)
        right_layout.addWidget(self.entry_table)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Bottom panel - Entry details
        details_widget = QWidget()
        details_layout = QFormLayout()
        details_widget.setLayout(details_layout)
        
        self.detail_title = QLabel()
        self.detail_username = QLabel()
        self.detail_password = QLineEdit()
        self.detail_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.detail_password.setReadOnly(True)
        self.detail_url = QLabel()
        self.detail_tags = QLabel()
        self.detail_notes = QTextEdit()
        self.detail_notes.setReadOnly(True)
        self.detail_notes.setMaximumHeight(80)
        
        details_layout.addRow("Title:", self.detail_title)
        details_layout.addRow("Username:", self.detail_username)
        details_layout.addRow("Password:", self.detail_password)
        details_layout.addRow("URL:", self.detail_url)
        details_layout.addRow("Tags:", self.detail_tags)
        details_layout.addRow("Notes:", self.detail_notes)
        
        # Toggle password visibility button
        password_layout = QHBoxLayout()
        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.clicked.connect(self._toggle_password_visibility)
        self.copy_password_btn = QPushButton("Copy")
        self.copy_password_btn.clicked.connect(self._copy_password)
        password_layout.addWidget(self.detail_password)
        password_layout.addWidget(self.toggle_password_btn)
        password_layout.addWidget(self.copy_password_btn)
        
        main_layout.addWidget(details_widget)
        
        # Set fonts
        font = QFont("Arial", 10)
        self.setFont(font)
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Database...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_database)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Database...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_database)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save Database", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_database)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Import/Export submenu
        import_action = QAction("&Import from CSV...", self)
        import_action.triggered.connect(self._import_csv)
        file_menu.addAction(import_action)
        
        import_kdbx_action = QAction("Import from &KDBX...", self)
        import_kdbx_action.triggered.connect(self._import_kdbx)
        file_menu.addAction(import_kdbx_action)
        
        export_action = QAction("&Export to CSV...", self)
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Entry menu
        entry_menu = menubar.addMenu("&Entry")
        
        add_entry_action = QAction("&Add Entry...", self)
        add_entry_action.setShortcut("Ctrl+E")
        add_entry_action.triggered.connect(self._add_entry)
        entry_menu.addAction(add_entry_action)
        
        edit_entry_action = QAction("&Edit Entry...", self)
        edit_entry_action.triggered.connect(self._edit_entry)
        entry_menu.addAction(edit_entry_action)
        
        delete_entry_action = QAction("&Delete Entry", self)
        delete_entry_action.setShortcut("Delete")
        delete_entry_action.triggered.connect(self._delete_entry)
        entry_menu.addAction(delete_entry_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        generate_password_action = QAction("&Generate Password...", self)
        generate_password_action.setShortcut("Ctrl+G")
        generate_password_action.triggered.connect(self._generate_password)
        tools_menu.addAction(generate_password_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Add actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self._new_database)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_database)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self._save_database)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        add_entry_action = QAction("Add Entry", self)
        add_entry_action.triggered.connect(self._add_entry)
        toolbar.addAction(add_entry_action)
        
        edit_entry_action = QAction("Edit Entry", self)
        edit_entry_action.triggered.connect(self._edit_entry)
        toolbar.addAction(edit_entry_action)
        
        delete_entry_action = QAction("Delete Entry", self)
        delete_entry_action.triggered.connect(self._delete_entry)
        toolbar.addAction(delete_entry_action)
    
    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")
    
    def _new_database(self):
        """Create a new database."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Create New Database",
            "",
            "KeePass Database (*.kdbx)"
        )
        
        if not filepath:
            return
        
        password, ok = QInputDialog.getText(
            self,
            "Master Password",
            "Enter master password:",
            QLineEdit.EchoMode.Password
        )
        
        if not ok or not password:
            return
        
        password_confirm, ok = QInputDialog.getText(
            self,
            "Confirm Password",
            "Confirm master password:",
            QLineEdit.EchoMode.Password
        )
        
        if not ok or password != password_confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match!")
            return
        
        if self.db_manager.create(filepath, password):
            self.statusBar().showMessage(f"Database created: {filepath}")
            self._load_database()
        else:
            QMessageBox.critical(self, "Error", "Failed to create database!")
    
    def _open_database(self):
        """Open an existing database."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Database",
            "",
            "KeePass Database (*.kdbx)"
        )
        
        if not filepath:
            return
        
        password, ok = QInputDialog.getText(
            self,
            "Master Password",
            "Enter master password:",
            QLineEdit.EchoMode.Password
        )
        
        if not ok or not password:
            return
        
        if self.db_manager.open(filepath, password):
            self.statusBar().showMessage(f"Database opened: {filepath}")
            self._load_database()
        else:
            QMessageBox.critical(self, "Error", "Failed to open database!\nCheck your password.")
    
    def _save_database(self):
        """Save the current database."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        if self.db_manager.save():
            self.statusBar().showMessage("Database saved")
        else:
            QMessageBox.critical(self, "Error", "Failed to save database!")
    
    def _load_database(self):
        """Load database contents into UI."""
        self.group_tree.clear()
        self.entry_table.setRowCount(0)
        
        if not self.db_manager.is_open():
            return
        
        # Load groups
        root_item = QTreeWidgetItem(self.group_tree, ["Database"])
        self._load_groups(self.db_manager.kp.root_group, root_item)
        self.group_tree.expandAll()
        
        # Load all entries
        self._load_entries()
    
    def _load_groups(self, group, parent_item):
        """Recursively load groups into tree."""
        for subgroup in group.subgroups:
            item = QTreeWidgetItem(parent_item, [subgroup.name])
            item.setData(0, Qt.ItemDataRole.UserRole, subgroup)
            self._load_groups(subgroup, item)
    
    def _load_entries(self, group=None):
        """Load entries into table."""
        self.entry_table.setRowCount(0)
        
        if not self.db_manager.is_open():
            return
        
        # Get entries
        if group:
            entries = group.entries
        else:
            entries = self.db_manager.get_entries()
        
        # Populate table
        self.entry_table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.entry_table.setItem(i, 0, QTableWidgetItem(entry.title or ""))
            self.entry_table.setItem(i, 1, QTableWidgetItem(entry.username or ""))
            self.entry_table.setItem(i, 2, QTableWidgetItem(entry.url or ""))
            self.entry_table.setItem(i, 3, QTableWidgetItem(entry.tags or ""))
            self.entry_table.setItem(i, 4, QTableWidgetItem(str(entry.mtime) if entry.mtime else ""))
            
            # Store entry object
            self.entry_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, entry)
    
    def _on_group_selected(self, item):
        """Handle group selection."""
        group = item.data(0, Qt.ItemDataRole.UserRole)
        if group:
            self._load_entries(group)
    
    def _on_search(self, text):
        """Handle search input."""
        if not self.db_manager.is_open():
            return
        
        if text:
            entries = self.db_manager.get_entries(search=text)
        else:
            entries = self.db_manager.get_entries()
        
        self.entry_table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.entry_table.setItem(i, 0, QTableWidgetItem(entry.title or ""))
            self.entry_table.setItem(i, 1, QTableWidgetItem(entry.username or ""))
            self.entry_table.setItem(i, 2, QTableWidgetItem(entry.url or ""))
            self.entry_table.setItem(i, 3, QTableWidgetItem(entry.tags or ""))
            self.entry_table.setItem(i, 4, QTableWidgetItem(str(entry.mtime) if entry.mtime else ""))
            self.entry_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, entry)
    
    def _on_entry_double_clicked(self):
        """Handle entry double-click."""
        self._show_entry_details()
    
    def _show_entry_details(self):
        """Show selected entry details."""
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            return
        
        entry = self.entry_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.detail_title.setText(entry.title or "")
        self.detail_username.setText(entry.username or "")
        self.detail_password.setText(entry.password or "")
        self.detail_url.setText(entry.url or "")
        self.detail_tags.setText(entry.tags or "")
        self.detail_notes.setText(entry.notes or "")
    
    def _toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.detail_password.echoMode() == QLineEdit.EchoMode.Password:
            self.detail_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.detail_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("Show")
    
    def _copy_password(self):
        """Copy password to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.detail_password.text())
        self.statusBar().showMessage("Password copied to clipboard", 2000)
    
    def _add_entry(self):
        """Add a new entry."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        dialog = EntryDialog(self, self.password_generator)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.add_entry(
                data['group'],
                data['title'],
                data['username'],
                data['password'],
                data['url'],
                data['notes'],
                data.get('tags'),
                data.get('icon')
            ):
                self.statusBar().showMessage("Entry added")
                self._load_entries()
            else:
                QMessageBox.critical(self, "Error", "Failed to add entry!")
    
    def _edit_entry(self):
        """Edit selected entry."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "No entry selected!")
            return
        
        entry = self.entry_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = EntryDialog(self, self.password_generator, entry)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.update_entry(
                entry,
                title=data['title'],
                username=data['username'],
                password=data['password'],
                url=data['url'],
                notes=data['notes'],
                tags=data.get('tags'),
                icon=data.get('icon')
            ):
                # Prompt to save changes
                reply = QMessageBox.question(
                    self,
                    "Save Changes",
                    "Do you want to save the changes to the database?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.db_manager.save()
                    self.statusBar().showMessage("Entry updated and saved")
                else:
                    self.statusBar().showMessage("Entry updated (not saved)")
                    
                self._load_entries()
            else:
                QMessageBox.critical(self, "Error", "Failed to update entry!")
    
    def _delete_entry(self):
        """Delete selected entry."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "No entry selected!")
            return
        
        entry = self.entry_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{entry.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Ask if user wants to move to recycle bin or permanently delete
            recycle_reply = QMessageBox.question(
                self,
                "Delete Method",
                "Move to recycle bin (safer) or permanently delete?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            use_recycle_bin = (recycle_reply == QMessageBox.StandardButton.Yes)
            
            if self.db_manager.delete_entry(entry, use_recycle_bin=use_recycle_bin):
                msg = "Entry moved to recycle bin" if use_recycle_bin else "Entry permanently deleted"
                self.statusBar().showMessage(msg)
                self._load_entries()
                self._clear_details()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete entry!")
    
    def _clear_details(self):
        """Clear entry details panel."""
        self.detail_title.setText("")
        self.detail_username.setText("")
        self.detail_password.setText("")
        self.detail_url.setText("")
        self.detail_tags.setText("")
        self.detail_notes.setText("")
    
    def _generate_password(self):
        """Show password generator dialog."""
        dialog = PasswordGeneratorDialog(self, self.password_generator)
        dialog.exec()
    
    def _export_csv(self):
        """Export database to CSV."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            "",
            "CSV Files (*.csv)"
        )
        
        if not filepath:
            return
        
        reply = QMessageBox.question(
            self,
            "Include Passwords",
            "Do you want to include passwords in the export?\n(Warning: CSV files are not encrypted!)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        include_passwords = (reply == QMessageBox.StandardButton.Yes)
        
        if self.db_manager.export_to_csv(filepath, include_passwords):
            QMessageBox.information(self, "Success", f"Database exported to {filepath}")
        else:
            QMessageBox.critical(self, "Error", "Failed to export database!")
    
    def _import_csv(self):
        """Import entries from CSV."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import from CSV",
            "",
            "CSV Files (*.csv)"
        )
        
        if not filepath:
            return
        
        results = self.db_manager.import_from_csv(filepath)
        
        if 'error' in results:
            QMessageBox.critical(self, "Error", results['error'])
        else:
            msg = f"Import completed:\n"
            msg += f"Successfully imported: {results['success']}\n"
            msg += f"Failed: {results['failed']}\n"
            msg += f"Duplicates skipped: {len(results['duplicates'])}"
            
            if results.get('errors'):
                msg += f"\n\nErrors:\n" + "\n".join(results['errors'][:5])
            
            QMessageBox.information(self, "Import Results", msg)
            self._load_entries()
    
    def _import_kdbx(self):
        """Import entries from another KDBX database."""
        if not self.db_manager.is_open():
            QMessageBox.warning(self, "Warning", "No database is open!")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import from KDBX",
            "",
            "KeePass Database (*.kdbx)"
        )
        
        if not filepath:
            return
        
        password, ok = QInputDialog.getText(
            self,
            "Source Database Password",
            "Enter password for source database:",
            QLineEdit.EchoMode.Password
        )
        
        if not ok or not password:
            return
        
        results = self.db_manager.import_from_kdbx(filepath, password)
        
        if 'error' in results:
            QMessageBox.critical(self, "Error", results['error'])
        else:
            msg = f"Import completed:\n"
            msg += f"Successfully imported: {results['success']}\n"
            msg += f"Failed: {results['failed']}\n"
            msg += f"Duplicates found: {len(results['duplicates'])}"
            
            if results['duplicates']:
                msg += f"\n\nDuplicate entries were skipped. Review the database to merge if needed."
            
            if results.get('errors'):
                msg += f"\n\nErrors:\n" + "\n".join(results['errors'][:5])
            
            QMessageBox.information(self, "Import Results", msg)
            self._load_entries()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.db_manager.modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.db_manager.save():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About KeyPy",
            "<h2>KeyPy v0.1.0</h2>"
            "<p>A Python port of KeePassXC password manager</p>"
            "<p>Copyright © 2026 Saurabh Sharma</p>"
            "<p>Licensed under MIT License</p>"
        )


class EntryDialog(QDialog):
    """Dialog for adding/editing entries."""
    
    def __init__(self, parent, password_generator, entry=None):
        """Initialize entry dialog."""
        super().__init__(parent)
        
        self.password_generator = password_generator
        self.entry = entry
        
        self.setWindowTitle("Edit Entry" if entry else "Add Entry")
        self.setModal(True)
        self.resize(500, 400)
        
        self._setup_ui()
        
        if entry:
            self._load_entry_data()
    
    def _setup_ui(self):
        """Set up dialog UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form
        form_layout = QFormLayout()
        
        self.group_input = QLineEdit("Root")
        self.title_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.url_input = QLineEdit()
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Comma-separated tags (e.g., work, important)")
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        
        # Icon selection (simplified - using standard icon names)
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Icon number (0-68) or leave empty for default")
        
        form_layout.addRow("Group:", self.group_input)
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Username:", self.username_input)
        
        # Password with generate button
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self._generate_password)
        password_layout.addWidget(generate_btn)
        form_layout.addRow("Password:", password_layout)
        
        form_layout.addRow("URL:", self.url_input)
        form_layout.addRow("Tags:", self.tags_input)
        form_layout.addRow("Icon:", self.icon_input)
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _load_entry_data(self):
        """Load entry data into form."""
        if not self.entry:
            return
        
        self.group_input.setText(self.entry.group.name if self.entry.group else "Root")
        self.title_input.setText(self.entry.title or "")
        self.username_input.setText(self.entry.username or "")
        self.password_input.setText(self.entry.password or "")
        self.url_input.setText(self.entry.url or "")
        self.tags_input.setText(self.entry.tags or "")
        self.icon_input.setText(str(self.entry.icon) if self.entry.icon else "")
        self.notes_input.setText(self.entry.notes or "")
    
    def _generate_password(self):
        """Generate a password."""
        password = self.password_generator.generate()
        self.password_input.setText(password)
    
    def get_data(self):
        """Get form data."""
        return {
            'group': self.group_input.text(),
            'title': self.title_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'url': self.url_input.text(),
            'tags': self.tags_input.text(),
            'icon': self.icon_input.text(),
            'notes': self.notes_input.toPlainText()
        }


class PasswordGeneratorDialog(QDialog):
    """Dialog for password generation."""
    
    def __init__(self, parent, password_generator):
        """Initialize password generator dialog."""
        super().__init__(parent)
        
        self.password_generator = password_generator
        
        self.setWindowTitle("Generate Password")
        self.setModal(True)
        self.resize(500, 300)
        
        self._setup_ui()
        self._generate_password()
    
    def _setup_ui(self):
        """Set up dialog UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Generated password display
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Courier", 12))
        layout.addWidget(QLabel("Generated Password:"))
        layout.addWidget(self.password_display)
        
        # Strength indicator
        self.strength_label = QLabel()
        layout.addWidget(self.strength_label)
        
        # Options
        options_layout = QFormLayout()
        
        self.length_spin = QSpinBox()
        self.length_spin.setMinimum(4)
        self.length_spin.setMaximum(128)
        self.length_spin.setValue(16)
        self.length_spin.valueChanged.connect(self._generate_password)
        options_layout.addRow("Length:", self.length_spin)
        
        self.lowercase_check = QCheckBox()
        self.lowercase_check.setChecked(True)
        self.lowercase_check.stateChanged.connect(self._generate_password)
        options_layout.addRow("Lowercase (a-z):", self.lowercase_check)
        
        self.uppercase_check = QCheckBox()
        self.uppercase_check.setChecked(True)
        self.uppercase_check.stateChanged.connect(self._generate_password)
        options_layout.addRow("Uppercase (A-Z):", self.uppercase_check)
        
        self.digits_check = QCheckBox()
        self.digits_check.setChecked(True)
        self.digits_check.stateChanged.connect(self._generate_password)
        options_layout.addRow("Digits (0-9):", self.digits_check)
        
        self.special_check = QCheckBox()
        self.special_check.setChecked(True)
        self.special_check.stateChanged.connect(self._generate_password)
        options_layout.addRow("Special characters:", self.special_check)
        
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        regenerate_btn = QPushButton("Regenerate")
        regenerate_btn.clicked.connect(self._generate_password)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self._copy_password)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(regenerate_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _generate_password(self):
        """Generate a new password."""
        try:
            password = self.password_generator.generate(
                length=self.length_spin.value(),
                use_lowercase=self.lowercase_check.isChecked(),
                use_uppercase=self.uppercase_check.isChecked(),
                use_digits=self.digits_check.isChecked(),
                use_special=self.special_check.isChecked()
            )
            
            self.password_display.setText(password)
            
            # Show strength
            strength = self.password_generator.assess_strength(password)
            self.strength_label.setText(
                f"Strength: {strength['strength']} ({strength['entropy']:.1f} bits)"
            )
        except ValueError as e:
            self.password_display.setText("")
            self.strength_label.setText(f"Error: {e}")
    
    def _copy_password(self):
        """Copy password to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password_display.text())
        self.strength_label.setText("Password copied to clipboard!")


def main():
    """Main entry point for GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("KeyPy")
    app.setOrganizationName("KeyPy")
    
    window = KeyPyMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
