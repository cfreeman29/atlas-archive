import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QDialog, QFileDialog,
                           QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer

from src.utils import Database, LogParser, ItemParser
from src.dialogs import (BossKillDialog, MapCompletionDialog, MapRunsDialog, 
                        ItemEntryDialog)

class MapTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PoE2 Map Tracker")
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
        layout.addStretch()

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
                # If RIP and map has a boss, ask if they killed the boss
                has_boss = self.current_map_start['has_boss']
                if completion_status == 'rip' and has_boss:
                    boss_dialog = BossKillDialog(self)
                    boss_result = boss_dialog.exec()
                    has_boss = boss_result == 1  # Yes = 1, No = 2
                
                duration_seconds = int(self.current_map_duration.total_seconds())
                self.db.add_map_run(
                    self.current_map_start['map_name'],
                    has_boss,
                    self.current_map_start['timestamp'],
                    duration_seconds,
                    [],  # Items will be added later
                    completion_status
                )
                self.current_map_start = None
                self.current_map_seed = None
                self.current_map_duration = timedelta()
                status_text = "Complete" if completion_status == 'complete' else "RIP"
                self.map_name_label.setText(f"Map {status_text}")
                self.end_map_btn.hide()
                self.log_items_btn.show()

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
    window = MapTracker()
    window.show()
    sys.exit(app.exec())
