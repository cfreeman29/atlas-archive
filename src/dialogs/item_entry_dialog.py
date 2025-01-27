from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication

class ItemEntryDialog(QDialog):
    def __init__(self, item_parser, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Map Items")
        self.setMinimumWidth(400)
        self.items = []
        self.item_parser = item_parser
        self.setup_ui()
        self.setup_clipboard_monitoring()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Ctrl+C items from the game.\nThey will be automatically added to the list.")
        instructions.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(instructions)
        
        # Items list in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
                border-radius: 4px;
                min-height: 200px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #4d4d4d;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(5)
        self.items_layout.setContentsMargins(10, 10, 10, 10)
        
        self.items_label = QLabel("Items: None")
        self.items_label.setStyleSheet("color: #cccccc;")
        self.items_layout.addWidget(self.items_label)
        self.items_layout.addStretch()
        
        scroll_area.setWidget(self.items_widget)
        layout.addWidget(scroll_area)
        
        # Done button
        self.done_btn = QPushButton("Done")
        self.done_btn.clicked.connect(self.accept)
        layout.addWidget(self.done_btn)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: #8b0000;
                border: none;
                padding: 8px 16px;
                color: white !important;
                border-radius: 4px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        
    def setup_clipboard_monitoring(self):
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.handle_clipboard)
        
    def handle_clipboard(self):
        text = self.clipboard.text()
        if text:
            new_items = self.item_parser.parse_items(text)
            if new_items:
                # Add new items to existing items
                self.items.extend(new_items)
                # Let ItemParser handle the combining when we display
                combined_items = self.item_parser.parse_items("\n--------\n".join(
                    f"Item Class: {item['item_class']}\n"
                    f"Rarity: {item['rarity']}\n"
                    f"{item['name']}\n"
                    f"Stack Size: {item['stack_size']}"
                    for item in self.items
                ))
                self.items = combined_items
                self.update_items_display()
                
    def update_items_display(self):
        # Clear existing items
        for i in reversed(range(self.items_layout.count())):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not self.items:
            no_items = QLabel("Items: None")
            no_items.setStyleSheet("color: #cccccc;")
            self.items_layout.addWidget(no_items)
            self.items_layout.addStretch()
            return
        
        # Add header
        header = QLabel("Items:")
        header.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.items_layout.addWidget(header)
        
        # Add items
        for item in self.items:
            name = item.get('name', 'Unknown')
            # Skip items with system text
            if (name != 'Unknown Item' and 
                not name.startswith('Item Class:') and 
                not name.startswith('Stack Size:') and 
                not name.startswith('Rarity:')):
                quantity = item.get('stack_size', 1)
                item_label = QLabel(f"{name} x{quantity}")
                item_label.setStyleSheet("color: #cccccc;")
                self.items_layout.addWidget(item_label)
        
        self.items_layout.addStretch()
