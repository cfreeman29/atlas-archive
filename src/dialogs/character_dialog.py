from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QComboBox, QSpinBox, QListWidget,
                           QListWidgetItem, QMessageBox)
from .edit_character_dialog import EditCharacterDialog
from PyQt6.QtCore import Qt, pyqtSignal

class CharacterDialog(QDialog):
    character_selected = pyqtSignal(int)  # Emits character ID when selected
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Character Selection")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_characters()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Character List
        self.character_list = QListWidget()
        self.character_list.itemDoubleClicked.connect(self.select_character)
        layout.addWidget(QLabel("Characters:"))
        layout.addWidget(self.character_list)
        
        # New Character Section
        new_char_layout = QVBoxLayout()
        new_char_layout.addWidget(QLabel("Create New Character"))
        
        # Name input
        name_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Character Name")
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.name_input)
        new_char_layout.addLayout(name_layout)
        
        # Class selection
        class_layout = QHBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems([
            "Warrior", "Ranger", "Witch", "Sorceress", "Mercenary", "Monk"
        ])
        class_layout.addWidget(QLabel("Class:"))
        class_layout.addWidget(self.class_combo)
        new_char_layout.addLayout(class_layout)
        
        # Level input
        level_layout = QHBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(1)
        level_layout.addWidget(QLabel("Level:"))
        level_layout.addWidget(self.level_spin)
        new_char_layout.addLayout(level_layout)
        
        # Ascendancy selection
        ascendancy_layout = QHBoxLayout()
        self.ascendancy_combo = QComboBox()
        self.ascendancy_combo.setEnabled(False)  # Enable after class selection
        self.class_combo.currentTextChanged.connect(self.update_ascendancies)
        ascendancy_layout.addWidget(QLabel("Ascendancy:"))
        ascendancy_layout.addWidget(self.ascendancy_combo)
        new_char_layout.addLayout(ascendancy_layout)
        
        layout.addLayout(new_char_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Character")
        create_btn.clicked.connect(self.create_character)
        button_layout.addWidget(create_btn)
        
        select_btn = QPushButton("Select Character")
        select_btn.clicked.connect(lambda: self.select_character(self.character_list.currentItem()))
        button_layout.addWidget(select_btn)
        
        edit_btn = QPushButton("Edit Character")
        edit_btn.clicked.connect(self.edit_character)
        button_layout.addWidget(edit_btn)
        
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
                padding: 5px 25px 5px 5px;  /* Extra padding on the right for arrows */
                border-radius: 3px;
                min-height: 24px;  /* Ensure minimum height */
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;  /* Make the up/down buttons wider */
                height: 16px;  /* Make the buttons taller */
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
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #8b0000;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
    
    def update_ascendancies(self, class_name):
        self.ascendancy_combo.clear()
        ascendancies = {
            "Warrior": ["Titan", "Warbringer"],
            "Ranger": ["Deadeye", "Pathfinder"],
            "Witch": ["Infernalist", "Blood Mage"],
            "Sorceress": ["Stormweaver", "Chronomancer"],
            "Mercenary": ["Witchhunter", "Gemling Legionnaire"],
            "Monk": ["Invoker", "Acolyte of Chayula"]
        }
        self.ascendancy_combo.addItems(ascendancies.get(class_name, []))
        self.ascendancy_combo.setEnabled(True)
    
    def load_characters(self):
        self.character_list.clear()
        characters = self.db.get_characters()
        for char in characters:
            item = QListWidgetItem(f"{char['name']} (Level {char['level']} {char['class']}"
                                 f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''})")
            item.setData(Qt.ItemDataRole.UserRole, char['id'])
            self.character_list.addItem(item)
    
    def create_character(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a character name")
            return
            
        char_class = self.class_combo.currentText()
        level = self.level_spin.value()
        ascendancy = self.ascendancy_combo.currentText() if self.ascendancy_combo.isEnabled() else None
        
        char_id = self.db.add_character(name, char_class, level, ascendancy)
        self.load_characters()
        
        # Select the newly created character
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == char_id:
                self.character_list.setCurrentItem(item)
                break
    
    def select_character(self, item):
        if item:
            char_id = item.data(Qt.ItemDataRole.UserRole)
            self.character_selected.emit(char_id)
            self.accept()
            
    def edit_character(self):
        item = self.character_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a character to edit")
            return
            
        char_id = item.data(Qt.ItemDataRole.UserRole)
        dialog = EditCharacterDialog(self.db, char_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_characters()  # Refresh the list to show updated info
