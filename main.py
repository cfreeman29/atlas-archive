import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QDialog, QFileDialog,
                           QDialogButtonBox, QSpinBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QCursor, QIcon

from src.utils.database import Database
from src.utils.log_parser import LogParser
from src.utils.item_parser import ItemParser
from src.utils.resource_path import get_resource_path
from src.dialogs.boss_kill_dialog import BossKillDialog
from src.dialogs.map_completion_dialog import MapCompletionDialog
from src.dialogs.map_runs_dialog import MapRunsDialog
from src.dialogs.item_entry_dialog import ItemEntryDialog

class ClickableLabel(QLabel):
    def __init__(self, base_path, parent=None):
        super().__init__(parent)
        self.active = False
        # Store paths for both states
        self.active_pixmap = QPixmap(get_resource_path(base_path))
        self.inactive_pixmap = QPixmap(get_resource_path(base_path.replace('.png', '_off.png')))
        self.setFixedSize(48, 48)  # Set fixed size for the icons
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # Change cursor on hover
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
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.active = not self.active
            self.update_pixmap()
            
    def is_active(self):
        return self.active
    
    def set_active(self, active):
        if self.active != active:
            self.active = active
            self.update_pixmap()

class MapTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atlas Archive")
        self.setMinimumSize(800, 400)
        
        # Initialize components
        self.db = Database()
        self.settings = self.load_settings()
        self.log_parser = LogParser(self.settings.get('log_path', None))
        self.item_parser = ItemParser()
        self.current_map_start = None
        self.current_map_seed = None
        self.current_map_duration = timedelta()
        self.monitoring = False
        self.map_timer = QTimer()
        self.map_timer.timeout.connect(self.update_map_timer)
        self.map_timer.setInterval(1000)  # Update every second
        
        # Setup UI
        self.setup_ui()
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QPushButton {
                background-color: #8b0000;
                border: none;
                padding: 8px 16px;
                color: white;
                border-radius: 4px;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
            QPushButton[monitoring="true"] {
                background-color: #006400;
            }
            QPushButton[monitoring="true"]:hover {
                background-color: #008000;
            }
            QPushButton.counter-btn {
                min-width: 25px;
                min-height: 25px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QLabel#map_name {
                font-size: 24px;
                font-weight: bold;
                color: #ff4444;
            }
            QLabel#timer {
                font-size: 20px;
                color: #ffffff;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 2px;
                width: 40px;
            }
            QSpinBox:disabled {
                color: #666666;
                border-color: #2d2d2d;
            }
        """)
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.monitor_btn = QPushButton("Start Monitoring")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.monitor_btn)
        
        self.select_log_btn = QPushButton("Select Client.txt")
        self.select_log_btn.clicked.connect(self.select_log_file)
        control_layout.addWidget(self.select_log_btn)
        
        self.view_runs_btn = QPushButton("View Runs")
        self.view_runs_btn.clicked.connect(self.show_runs_dialog)
        control_layout.addWidget(self.view_runs_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Current map info
        map_layout = QVBoxLayout()
        map_layout.setSpacing(10)
        
        self.map_name_label = QLabel("Not in map")
        self.map_name_label.setObjectName("map_name")
        map_layout.addWidget(self.map_name_label)
        
        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timer")
        self.timer_label.hide()
        map_layout.addWidget(self.timer_label)
        
        # Button layout for map controls
        map_buttons_layout = QHBoxLayout()
        
        self.end_map_btn = QPushButton("End Map")
        self.end_map_btn.clicked.connect(self.handle_manual_map_end)
        self.end_map_btn.hide()
        map_buttons_layout.addWidget(self.end_map_btn)
        
        self.log_items_btn = QPushButton("Log Items")
        self.log_items_btn.clicked.connect(self.show_item_entry_dialog)
        self.log_items_btn.hide()
        map_buttons_layout.addWidget(self.log_items_btn)
        
        map_buttons_layout.addStretch()
        map_layout.addLayout(map_buttons_layout)
        layout.addLayout(map_layout)
        
        # Add stretch to push mechanics to bottom
        layout.addStretch()
        
        # Mechanics section at bottom
        mechanics_layout = QHBoxLayout()
        mechanics_layout.setSpacing(20)
        
        # Breach section with counter
        breach_section = QHBoxLayout()
        self.breach_icon = ClickableLabel("src/images/endgame-mech/breach.png")
        self.breach_icon.hide()
        breach_section.addWidget(self.breach_icon)
        
        breach_counter = QHBoxLayout()
        self.breach_minus_btn = QPushButton("-")
        self.breach_minus_btn.setProperty("class", "counter-btn")
        self.breach_minus_btn.clicked.connect(lambda: self.adjust_breach_count(-1))
        self.breach_minus_btn.hide()
        
        self.breach_count_spin = QSpinBox()
        self.breach_count_spin.setRange(0, 10)
        self.breach_count_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.breach_count_spin.hide()
        self.breach_count_spin.setEnabled(False)
        
        self.breach_plus_btn = QPushButton("+")
        self.breach_plus_btn.setProperty("class", "counter-btn")
        self.breach_plus_btn.clicked.connect(lambda: self.adjust_breach_count(1))
        self.breach_plus_btn.hide()
        
        breach_counter.addWidget(self.breach_minus_btn)
        breach_counter.addWidget(self.breach_count_spin)
        breach_counter.addWidget(self.breach_plus_btn)
        breach_section.addLayout(breach_counter)
        mechanics_layout.addLayout(breach_section)
        
        # Other mechanics
        self.delirium_icon = ClickableLabel("src/images/endgame-mech/delirium.png")
        self.delirium_icon.hide()
        mechanics_layout.addWidget(self.delirium_icon)
        
        self.expedition_icon = ClickableLabel("src/images/endgame-mech/expedition.png")
        self.expedition_icon.hide()
        mechanics_layout.addWidget(self.expedition_icon)
        
        self.ritual_icon = ClickableLabel("src/images/endgame-mech/ritual.png")
        self.ritual_icon.hide()
        mechanics_layout.addWidget(self.ritual_icon)
        
        mechanics_layout.addStretch()
        layout.addLayout(mechanics_layout)

        # Connect breach icon click to counter toggle
        self.breach_icon.mousePressEvent = self.on_breach_icon_click

    def on_breach_icon_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.breach_icon.active = not self.breach_icon.active
            self.breach_icon.update_pixmap()
            self.breach_count_spin.setEnabled(self.breach_icon.active)
            self.breach_minus_btn.setEnabled(self.breach_icon.active)
            self.breach_plus_btn.setEnabled(self.breach_icon.active)
            if not self.breach_icon.active:
                self.breach_count_spin.setValue(0)

    def adjust_breach_count(self, delta):
        """Adjust breach count by delta amount"""
        current = self.breach_count_spin.value()
        self.breach_count_spin.setValue(max(0, min(10, current + delta)))

    def show_runs_dialog(self):
        dialog = MapRunsDialog(self.db, self)
        dialog.exec()

    def select_log_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Client.txt",
            str(Path.home()),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_name:
            # Update settings
            self.settings['log_path'] = file_name
            self.save_settings()
            
            # Update log parser
            self.log_parser = LogParser(file_name)
            self.map_name_label.setText(f"Log file selected: {Path(file_name).name}")
            
    def toggle_monitoring(self):
        if not self.monitoring:
            if not self.log_parser.log_path:
                self.map_name_label.setText("Please select Client.txt first")
                return
                
            self.monitoring = True
            self.monitor_btn.setText("Stop Monitoring")
            self.monitor_btn.setProperty("monitoring", "true")
            self.monitor_btn.setStyle(self.monitor_btn.style())
            self.setup_log_monitoring()
        else:
            self.monitoring = False
            self.monitor_btn.setText("Start Monitoring")
            self.monitor_btn.setProperty("monitoring", "false")
            self.monitor_btn.setStyle(self.monitor_btn.style())
            if hasattr(self, 'timer'):
                self.timer.stop()

    def setup_log_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_log_updates)
        self.timer.start(1000)  # Check every second

    def check_log_updates(self):
        if not self.monitoring:
            return
            
        log_events = self.log_parser.check_updates()
        for event in log_events:
            if event['type'] == 'map_start':
                self.handle_map_start(event)
            elif event['type'] == 'map_end':
                self.handle_map_end(event)

    def handle_map_start(self, event):
        # Extract seed from the event
        seed = event.get('seed')
        
        # If we have a current map and entering same instance
        if self.current_map_seed and seed == self.current_map_seed:
            # Continuing previous map instance
            self.current_map_start = event
            self.map_name_label.setText(f"In map: {event['map_name']} (Continued)")
        else:
            # Starting fresh map instance
            self.current_map_start = event
            self.current_map_seed = seed
            self.current_map_duration = timedelta()
            self.map_name_label.setText(f"In map: {event['map_name']}")
            
            # Reset mechanic selections for new map
            self.breach_icon.set_active(False)
            self.delirium_icon.set_active(False)
            self.expedition_icon.set_active(False)
            self.ritual_icon.set_active(False)
            self.breach_count_spin.setValue(0)
            
        # Show mechanic controls
        self.breach_icon.show()
        self.breach_count_spin.show()
        self.breach_minus_btn.show()
        self.breach_plus_btn.show()
        self.delirium_icon.show()
        self.expedition_icon.show()
        self.ritual_icon.show()
            
        # Reset UI state for map start
        self.timer_label.show()
        self.log_items_btn.hide()
        self.end_map_btn.hide()
        self.map_timer.start()

    def handle_map_end(self, event):
        if self.current_map_start:
            # Calculate duration of this segment
            segment_duration = event['timestamp'] - self.current_map_start['timestamp']
            self.current_map_duration += segment_duration
            
            # Stop the timer while we're out of the map
            self.map_timer.stop()
            
            next_area = event.get('next_area', '')
            if next_area.startswith('Hideout'):
                # Just temporarily in hideout, keep the map state
                self.map_name_label.setText(f"Map paused: {self.current_map_start['map_name']}")
                self.end_map_btn.show()  # Show end map button while paused
            else:
                # Actually leaving the map, consider it complete
                self.complete_map()

    def handle_manual_map_end(self):
        """Handle manual map completion when user clicks End Map button"""
        if self.current_map_start:
            self.complete_map()
            
    def complete_map(self):
        """Complete the current map and reset state"""
        if self.current_map_start:
            # Show completion dialog
            dialog = MapCompletionDialog(self)
            result = dialog.exec()
            
            # Get completion status
            completion_status = 'complete' if result == 1 else 'rip' if result == 2 else None
            
            if completion_status:
                # Get boss count
                boss_count = 0  # Default to 0 for no boss
                has_boss = self.current_map_start['has_boss']
                
                # If map has a boss and either completed or RIP with boss kill
                if has_boss:
                    if completion_status == 'complete':
                        # For completed maps with boss, ask if it was twin
                        boss_dialog = BossKillDialog(self)
                        boss_dialog.label.setText("Was it a twin boss?")
                        boss_dialog.yes_btn.clicked.disconnect()
                        boss_dialog.no_btn.clicked.disconnect()
                        boss_dialog.yes_btn.clicked.connect(lambda: boss_dialog.done(2))  # Twin boss = 2
                        boss_dialog.no_btn.clicked.connect(lambda: boss_dialog.done(1))   # Single boss = 1
                        boss_count = boss_dialog.exec()
                    elif completion_status == 'rip':
                        # For RIP, first ask if they killed boss
                        boss_dialog = BossKillDialog(self)
                        boss_count = boss_dialog.exec()
                
                duration_seconds = int(self.current_map_duration.total_seconds())
                self.db.add_map_run(
                    self.current_map_start['map_name'],
                    boss_count,
                    self.current_map_start['timestamp'],
                    duration_seconds,
                    [],  # Items will be added later
                    completion_status,
                    self.breach_icon.is_active(),
                    self.delirium_icon.is_active(),
                    self.expedition_icon.is_active(),
                    self.ritual_icon.is_active(),
                    self.breach_count_spin.value()
                )
                self.current_map_start = None
                self.current_map_seed = None
                self.current_map_duration = timedelta()
                status_text = "Complete" if completion_status == 'complete' else "RIP"
                self.map_name_label.setText(f"Map {status_text}")
                self.end_map_btn.hide()
                self.log_items_btn.show()
                
                # Hide mechanic controls
                self.breach_icon.hide()
                self.breach_count_spin.hide()
                self.breach_minus_btn.hide()
                self.breach_plus_btn.hide()
                self.delirium_icon.hide()
                self.expedition_icon.hide()
                self.ritual_icon.hide()

    def update_map_timer(self):
        if self.current_map_start:
            current_segment = datetime.now() - self.current_map_start['timestamp']
            total_duration = self.current_map_duration + current_segment
            minutes = int(total_duration.total_seconds()) // 60
            seconds = int(total_duration.total_seconds()) % 60
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def show_item_entry_dialog(self):
        dialog = ItemEntryDialog(self.item_parser, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.items:
            self.db.add_items_to_latest_map(dialog.items)
            self.log_items_btn.hide()
            self.map_name_label.setText("Not in map")
            self.timer_label.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_resource_path("src/images/app/icon.png")))
    window = MapTracker()
    window.setWindowIcon(QIcon(get_resource_path("src/images/app/icon.png")))
    window.show()
    sys.exit(app.exec())
