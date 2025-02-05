from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QListWidget, QListWidgetItem,
                           QMessageBox)
from PyQt6.QtCore import Qt
import re

class BuildManagerDialog(QDialog):
    def __init__(self, db, character_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.character_id = character_id
        self.character = self.db.get_character(character_id)
        
        self.setWindowTitle("Character Builds")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Character info header
        header = QLabel(
            f"Managing builds for: {self.character['name']} "
            f"(Level {self.character['level']} {self.character['class']}"
            f"{' - ' + self.character['ascendancy'] if self.character['ascendancy'] else ''})"
        )
        header.setStyleSheet("font-size: 14px; color: #44ff44; padding: 10px 0;")
        header.setWordWrap(True)
        layout.addWidget(header)
        
        # Build list section
        self.build_list = QListWidget()
        self.build_list.itemDoubleClicked.connect(self.edit_build)
        layout.addWidget(self.build_list)
        
        # Load builds after creating the list widget
        self.load_builds()
        
        # New build section
        new_build_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter build URL")
        new_build_layout.addWidget(self.url_input)
        
        add_btn = QPushButton("Add Build")
        add_btn.clicked.connect(self.add_build)
        new_build_layout.addWidget(add_btn)
        
        layout.addLayout(new_build_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit Build")
        edit_btn.clicked.connect(lambda: self.edit_build(self.build_list.currentItem()))
        button_layout.addWidget(edit_btn)
        
        set_current_btn = QPushButton("Set as Current")
        set_current_btn.clicked.connect(self.set_current_build)
        button_layout.addWidget(set_current_btn)
        
        delete_btn = QPushButton("Delete Build")
        delete_btn.clicked.connect(self.delete_build)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                padding: 8px 16px;
                color: white;
                border-radius: 4px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #4a4a4a;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)
        
    def validate_url(self, url):
        """Basic URL validation"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
        
    def load_builds(self):
        self.build_list.clear()
        builds = self.db.get_builds(self.character_id)
        for build in builds:
            item = QListWidgetItem(build['url'])
            if build['is_current']:
                item.setText(f"{build['url']} (Current)")
                item.setForeground(Qt.GlobalColor.green)
            item.setData(Qt.ItemDataRole.UserRole, build)
            self.build_list.addItem(item)
            
    def add_build(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a build URL")
            return
            
        if not self.validate_url(url):
            QMessageBox.warning(self, "Error", "Please enter a valid URL")
            return
            
        self.db.add_build(self.character_id, url)
        self.url_input.clear()
        self.load_builds()
        
    def edit_build(self, item):
        if not item:
            QMessageBox.warning(self, "Error", "Please select a build to edit")
            return
            
        build = item.data(Qt.ItemDataRole.UserRole)
        url, ok = QLineEdit.getText(
            self, 
            "Edit Build URL", 
            "Enter new URL:",
            QLineEdit.EchoMode.Normal,
            build['url']
        )
        
        if ok and url.strip():
            if not self.validate_url(url.strip()):
                QMessageBox.warning(self, "Error", "Please enter a valid URL")
                return
                
            self.db.update_build(build['id'], url.strip())
            self.load_builds()
            
    def delete_build(self):
        item = self.build_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a build to delete")
            return
            
        build = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this build?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_build(build['id'])
            self.load_builds()
            
    def set_current_build(self):
        item = self.build_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a build to set as current")
            return
            
        build = item.data(Qt.ItemDataRole.UserRole)
        self.db.set_current_build(self.character_id, build['id'])
        self.load_builds()
