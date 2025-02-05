from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QComboBox, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt

class EditCharacterDialog(QDialog):
    def __init__(self, db, character_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.character_id = character_id
        self.character = self.db.get_character(character_id)
        
        self.setWindowTitle(f"Edit Character - {self.character['name']}")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Name input
        name_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setText(self.character['name'])
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Class selection (disabled since it affects ascendancy)
        class_layout = QHBoxLayout()
        self.class_label = QLabel(self.character['class'])
        self.class_label.setStyleSheet("color: #888888;")  # Gray color to indicate it's not editable
        class_layout.addWidget(QLabel("Class:"))
        class_layout.addWidget(self.class_label)
        layout.addLayout(class_layout)
        
        # Level input
        level_layout = QHBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(self.character['level'])
        self.level_spin.setFixedWidth(100)
        self.level_spin.setFixedHeight(32)
        self.level_spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        level_layout.addWidget(QLabel("Level:"))
        level_layout.addWidget(self.level_spin)
        layout.addLayout(level_layout)
        
        # Ascendancy (disabled if already chosen)
        ascendancy_layout = QHBoxLayout()
        if self.character['ascendancy']:
            self.ascendancy_label = QLabel(self.character['ascendancy'])
            self.ascendancy_label.setStyleSheet("color: #888888;")  # Gray color to indicate it's not editable
            ascendancy_layout.addWidget(QLabel("Ascendancy:"))
            ascendancy_layout.addWidget(self.ascendancy_label)
        else:
            self.ascendancy_combo = QComboBox()
            ascendancies = {
                "Warrior": ["Titan", "Warbringer"],
                "Ranger": ["Deadeye", "Pathfinder"],
                "Witch": ["Infernalist", "Blood Mage"],
                "Sorceress": ["Stormweaver", "Chronomancer"],
                "Mercenary": ["Witchhunter", "Gemling Legionnaire"],
                "Monk": ["Invoker", "Acolyte of Chayula"]
            }
            self.ascendancy_combo.addItems(ascendancies.get(self.character['class'], []))
            ascendancy_layout.addWidget(QLabel("Ascendancy:"))
            ascendancy_layout.addWidget(self.ascendancy_combo)
        layout.addLayout(ascendancy_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px 25px 5px 5px;
                border-radius: 3px;
                min-height: 32px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                height: 16px;
            }
            QPushButton {
                background-color: #8b0000;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        
    def save_changes(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a character name")
            return
            
        level = self.level_spin.value()
        # Only update ascendancy if it wasn't already set
        ascendancy = None
        if not self.character['ascendancy'] and hasattr(self, 'ascendancy_combo'):
            ascendancy = self.ascendancy_combo.currentText()
            
        self.db.update_character(
            self.character_id,
            name=name,
            level=level,
            ascendancy=ascendancy
        )
        self.accept()
