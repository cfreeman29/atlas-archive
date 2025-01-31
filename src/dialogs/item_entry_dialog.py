from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QScrollArea, QWidget)
from PyQt6.QtCore import Qt, QTimer
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
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
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
        
        self.scroll_area.setWidget(self.items_widget)
        layout.addWidget(self.scroll_area)
        
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
            # Parse new items from clipboard
            new_items = self.item_parser.parse_items(text)
            if new_items:
                # Update existing items with new items
                for new_item in new_items:
                    name = new_item['name']
                    found = False
                    # Look for existing item with same name
                    for item in self.items:
                        if item['name'] == name:
                            # Update stack size
                            item['stack_size'] += new_item['stack_size']
                            found = True
                            break
                    if not found:
                        # Add new item if not found
                        self.items.append(new_item)
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
                rarity = item.get('display_rarity', 'Normal')
                
                # Extract name and rarity
                name_parts = name.rsplit('_', 1)
                display_name = name_parts[0]
                rarity = item.get('display_rarity', 'Normal')
                
                # Color mapping based on rarity and special suffixes
                rarity_colors = {
                    'Normal': '#ffffff',  # White
                    'Magic': '#8888ff',   # Blue
                    'Rare': '#ffff77',    # Yellow
                    'Unique': '#af6025',  # Orange/Brown
                    'Currency': '#aa9e82'  # Currency color
                }
                
                # Check for special suffixes
                if name.endswith('_pinkey'):
                    color = '#ff0000'  # Red for pinnacle keys
                elif name.endswith('_trials'):
                    color = '#b7410e'  # Rust color for trials items
                elif name.endswith('_gem'):
                    color = '#c0c0c0'  # Silver color for gems
                else:
                    color = rarity_colors.get(rarity, '#cccccc')
                item_label = QLabel(f"{display_name} x{quantity}")
                item_label.setStyleSheet(f"color: {color};")
                self.items_layout.addWidget(item_label)
        
        self.items_layout.addStretch()
        
        # Scroll to bottom after a brief delay to ensure layout is updated
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Scroll the view to the bottom"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
