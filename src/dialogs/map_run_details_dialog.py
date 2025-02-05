from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QGridLayout, QWidget, QScrollArea, QFileDialog, QMessageBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.utils.resource_path import get_resource_path
from src.utils.card_generator import generate_map_run_card

class MechanicIcon(QLabel):
    def __init__(self, base_path, active=False, parent=None):
        super().__init__(parent)
        # Store paths for both states
        self.active_pixmap = QPixmap(get_resource_path(base_path))
        self.inactive_pixmap = QPixmap(get_resource_path(base_path.replace('.png', '_off.png')))
        self.setFixedSize(32, 32)  # Set fixed size for the icons
        self.active = active
        self.update_pixmap()
        
    def update_pixmap(self):
        # Use the appropriate pixmap based on state
        pixmap = self.active_pixmap if self.active else self.inactive_pixmap
        # Scale the pixmap
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

class MapRunDetailsDialog(QDialog):
    def __init__(self, run_data, parent=None):
        super().__init__(parent)
        self.run_data = run_data
        self.db = parent.db if parent else None
        self.setWindowTitle(f"Map Run Details - {run_data['map_name']}")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Map Info Section
        info_widget = QWidget()
        info_layout = QGridLayout(info_widget)
        info_layout.setSpacing(10)
        
        # Map Name and Level
        map_header = QWidget()
        map_header_layout = QHBoxLayout(map_header)
        map_header_layout.setSpacing(10)
        
        map_name = QLabel(self.run_data['map_name'])
        map_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff4444;")
        map_header_layout.addWidget(map_name)
        
        map_level = QLabel(f"Level {self.run_data['map_level']}")
        map_level.setStyleSheet("font-size: 16px; color: #888888;")
        map_header_layout.addWidget(map_level)
        map_header_layout.addStretch()
        
        info_layout.addWidget(map_header, 0, 0, 1, 2)
        
        # Start Time
        start_time = datetime.fromisoformat(self.run_data['start_time'])
        info_layout.addWidget(QLabel("Start Time:"), 1, 0)
        info_layout.addWidget(QLabel(start_time.strftime('%Y-%m-%d %H:%M:%S')), 1, 1)
        
        # Duration
        duration_mins = self.run_data['duration'] // 60
        duration_secs = self.run_data['duration'] % 60
        info_layout.addWidget(QLabel("Duration:"), 2, 0)
        info_layout.addWidget(QLabel(f"{duration_mins:02d}:{duration_secs:02d}"), 2, 1)
        
        # Character Info
        if self.run_data.get('character_id') and self.db:
            char = self.db.get_character(self.run_data['character_id'])
            if char:
                info_layout.addWidget(QLabel("Character:"), 3, 0)
                char_label = QLabel(f"{char['name']} (Level {char['level']} {char['class']}"
                                  f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''})")
                char_label.setStyleSheet("color: #44ff44;")
                info_layout.addWidget(char_label, 3, 1)
        
        # Boss Count
        info_layout.addWidget(QLabel("Boss Status:"), 4, 0)
        boss_text = "No Boss"
        if self.run_data['boss_count'] == 1:
            boss_text = "Single Boss"
        elif self.run_data['boss_count'] == 2:
            boss_text = "Twin Boss"
        info_layout.addWidget(QLabel(boss_text), 4, 1)
        
        # Status
        status_text = "Complete" if self.run_data['completion_status'] == 'complete' else "RIP"
        status_color = "#006400" if self.run_data['completion_status'] == 'complete' else "#8b0000"
        info_layout.addWidget(QLabel("Status:"), 5, 0)
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        info_layout.addWidget(status_label, 5, 1)
        
        layout.addWidget(info_widget)
        
        # Mechanics Section
        mechanics_label = QLabel("Map Mechanics")
        mechanics_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(mechanics_label)
        
        mechanics_widget = QWidget()
        mechanics_layout = QHBoxLayout(mechanics_widget)
        mechanics_layout.setSpacing(20)
        
        # Add mechanics icons
        # Breach with counter
        breach_section = QHBoxLayout()
        breach_icon = MechanicIcon("src/images/endgame-mech/breach.png", self.run_data.get('has_breach', False))
        breach_section.addWidget(breach_icon)
        if self.run_data.get('has_breach'):
            breach_count = QLabel(f"x{self.run_data.get('breach_count', 0)}")
            breach_count.setStyleSheet("color: #ffffff; font-size: 14px;")
            breach_section.addWidget(breach_count)
        mechanics_layout.addLayout(breach_section)
        
        # Other mechanics
        delirium_icon = MechanicIcon("src/images/endgame-mech/delirium.png", self.run_data.get('has_delirium', False))
        mechanics_layout.addWidget(delirium_icon)
        
        expedition_icon = MechanicIcon("src/images/endgame-mech/expedition.png", self.run_data.get('has_expedition', False))
        mechanics_layout.addWidget(expedition_icon)
        
        ritual_icon = MechanicIcon("src/images/endgame-mech/ritual.png", self.run_data.get('has_ritual', False))
        mechanics_layout.addWidget(ritual_icon)
        
        mechanics_layout.addStretch()
        layout.addWidget(mechanics_widget)
        
        # Items Section
        items_label = QLabel("Loot")
        items_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(items_label)
        
        # Create scrollable item list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
                border-radius: 4px;
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
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        for item in self.run_data['items']:
                if (item['name'] != 'Unknown Item' and 
                not item['name'].startswith('Item Class:') and 
                not item['name'].startswith('Stack Size:') and 
                not item['name'].startswith('Rarity:')):
                    # Extract name and rarity
                    name = item['name']
                    name_parts = name.rsplit('_', 1)
                    display_name = name_parts[0]
                    # Get rarity from name suffix if available, otherwise fallback to display_rarity
                    rarity = name_parts[1] if len(name_parts) > 1 else item.get('display_rarity', 'Normal')
                    
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
                    elif name.endswith('_socket'):
                        color = '#add8e6'  # Light blue color for socketables
                    elif name.endswith('_flask'):
                        color = rarity_colors.get(rarity, '#cccccc')  # Use rarity color for flasks
                    elif name.endswith('_charm'):
                        color = rarity_colors.get(rarity, '#cccccc')  # Use rarity color for charms
                    else:
                        color = rarity_colors.get(rarity, '#cccccc')
                    item_text = f"{display_name} x{item['stack_size']}"
                    item_label = QLabel(item_text)
                    item_label.setStyleSheet(f"color: {color};")
                    scroll_layout.addWidget(item_label)
        
        if not self.run_data['items']:
            no_items = QLabel("No items recorded")
            no_items.setStyleSheet("color: #666666; font-style: italic;")
            scroll_layout.addWidget(no_items)
            
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("Export as Image")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        export_btn.clicked.connect(self.export_as_image)
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        # Delete button
        delete_btn = QPushButton("Delete Run")
        delete_btn.clicked.connect(self.handle_delete)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #8b0000;
                border: none;
                padding: 8px 16px;
                color: white;
                border-radius: 4px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        
    def handle_delete(self):
        self.done(2)  # Use custom return code 2 to indicate deletion
        
    def export_as_image(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Map Run Card",
            f"map_run_{self.run_data['map_name']}_{self.run_data['map_level']}.png",
            "PNG Images (*.png)"
        )
        
        if file_name:
            # Add db reference to run_data for character info
            run_data_with_db = dict(self.run_data)
            run_data_with_db['db'] = self.db
            if generate_map_run_card(run_data_with_db, file_name):
                QMessageBox.information(
                    self,
                    "Export Successful",
                    "Map run card has been exported successfully."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    "Failed to generate map run card."
                )
