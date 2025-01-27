import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, QDialog,
                           QListWidget, QListWidgetItem, QGridLayout, QScrollArea,
                           QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont, QClipboard
import re
import csv
from log_parser import LogParser
from item_parser import ItemParser
from database import Database

class BossKillDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Boss Status")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Question label
        label = QLabel("Did you kill the boss before dying?")
        label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.yes_btn = QPushButton("Yes")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.yes_btn.clicked.connect(lambda: self.done(1))
        
        self.no_btn = QPushButton("No")
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        self.no_btn.clicked.connect(lambda: self.done(2))
        
        button_layout.addWidget(self.yes_btn)
        button_layout.addWidget(self.no_btn)
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)

class MapCompletionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Completion Status")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Status label
        label = QLabel("How did the map end?")
        label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.complete_btn = QPushButton("Complete")
        self.complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.complete_btn.clicked.connect(lambda: self.done(1))
        
        self.rip_btn = QPushButton("RIP")
        self.rip_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        self.rip_btn.clicked.connect(lambda: self.done(2))
        
        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.rip_btn)
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)

class MapRunDetailsDialog(QDialog):
    def __init__(self, run_data, parent=None):
        super().__init__(parent)
        self.run_data = run_data
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
        
        # Map Name
        map_name = QLabel(self.run_data['map_name'])
        map_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff4444;")
        info_layout.addWidget(map_name, 0, 0, 1, 2)
        
        # Start Time
        start_time = datetime.fromisoformat(self.run_data['start_time'])
        info_layout.addWidget(QLabel("Start Time:"), 1, 0)
        info_layout.addWidget(QLabel(start_time.strftime('%Y-%m-%d %H:%M:%S')), 1, 1)
        
        # Duration
        duration_mins = self.run_data['duration'] // 60
        duration_secs = self.run_data['duration'] % 60
        info_layout.addWidget(QLabel("Duration:"), 2, 0)
        info_layout.addWidget(QLabel(f"{duration_mins:02d}:{duration_secs:02d}"), 2, 1)
        
        # Has Boss
        info_layout.addWidget(QLabel("Boss Killed:"), 3, 0)
        info_layout.addWidget(QLabel("Yes" if self.run_data['has_boss'] else "No"), 3, 1)
        
        # Status
        status_text = "Complete" if self.run_data['completion_status'] == 'complete' else "RIP"
        status_color = "#006400" if self.run_data['completion_status'] == 'complete' else "#8b0000"
        info_layout.addWidget(QLabel("Status:"), 4, 0)
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        info_layout.addWidget(status_label, 4, 1)
        
        layout.addWidget(info_widget)
        
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
                item_text = f"{item['name']} x{item['stack_size']}"
                item_label = QLabel(item_text)
                item_label.setStyleSheet("color: #cccccc;")
                scroll_layout.addWidget(item_label)
        
        if not self.run_data['items']:
            no_items = QLabel("No items recorded")
            no_items.setStyleSheet("color: #666666; font-style: italic;")
            scroll_layout.addWidget(no_items)
            
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Delete button
        delete_btn = QPushButton("Delete Run")
        delete_btn.clicked.connect(self.handle_delete)
        layout.addWidget(delete_btn)
        
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

class MapRunsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Map Runs History")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_runs()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with stats
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 14px; color: #cccccc;")
        layout.addWidget(self.stats_label)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.show_run_details)
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:alternate {
                background-color: #333333;
            }
            QListWidget::item:selected {
                background-color: #4a4a4a;
            }
            QListWidget::item:hover {
                background-color: #404040;
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
        
    def load_runs(self):
        runs = self.db.get_map_runs()
        self.list_widget.clear()
        
        total_duration = 0
        total_maps = len(runs)
        total_bosses = sum(1 for run in runs if run['has_boss'])
        total_complete = sum(1 for run in runs if run['completion_status'] == 'complete')
        total_rips = sum(1 for run in runs if run['completion_status'] == 'rip')
        
        for run in runs:
            start_time = datetime.fromisoformat(run['start_time'])
            duration_mins = run['duration'] // 60
            duration_secs = run['duration'] % 60
            total_duration += run['duration']
            
            # Format item count
            item_count = len([item for item in run['items'] 
                            if item['name'] != 'Unknown Item'
                            and not item['name'].startswith('Item Class:')
                            and not item['name'].startswith('Stack Size:')
                            and not item['name'].startswith('Rarity:')])
            
            # Create list item with summary
            item_text = (f"{run['map_name']} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Duration: {duration_mins:02d}:{duration_secs:02d} | "
                        f"Boss: {'Yes' if run['has_boss'] else 'No'} | "
                        f"Items: {item_count} | "
                        f"Status: {'Complete' if run['completion_status'] == 'complete' else 'RIP'}")
            
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.ItemDataRole.UserRole, run)  # Store run data
            self.list_widget.addItem(list_item)
            
        # Update stats
        avg_duration = total_duration / total_maps if total_maps > 0 else 0
        avg_mins = int(avg_duration) // 60
        avg_secs = int(avg_duration) % 60
        
        self.stats_label.setText(
            f"Total Maps: {total_maps} | "
            f"Complete: {total_complete} | "
            f"RIP: {total_rips} | "
            f"Bosses Killed: {total_bosses} | "
            f"Average Duration: {avg_mins:02d}:{avg_secs:02d}"
        )
            
    def show_run_details(self, item):
        run_data = item.data(Qt.ItemDataRole.UserRole)
        dialog = MapRunDetailsDialog(run_data, self)
        result = dialog.exec()
        
        if result == 2:  # Delete was clicked
            self.db.delete_map_run(run_data['id'])
            self.load_runs()
        
    def export_to_csv(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Map Runs",
            str(Path.home() / "map_runs.csv"),
            "CSV Files (*.csv)"
        )
        
        if file_name:
            runs = self.db.get_map_runs()
            with open(file_name, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['ID', 'Map Name', 'Has Boss', 'Start Time', 'Duration', 'Items', 'Status'])
                # Write data
                for run in runs:
                    items_text = ", ".join(
                        f"{item['name']} x{item['stack_size']}" 
                        for item in run['items']
                        if item['name'] != 'Unknown Item'
                        and not item['name'].startswith('Item Class:')
                        and not item['name'].startswith('Stack Size:')
                        and not item['name'].startswith('Rarity:')
                    )
                    duration_mins = run['duration'] // 60
                    duration_secs = run['duration'] % 60
                    writer.writerow([
                        run['id'],
                        run['map_name'],
                        'Yes' if run['has_boss'] else 'No',
                        run['start_time'],
                        f"{duration_mins:02d}:{duration_secs:02d}",
                        items_text if items_text else "None",
                        'Complete' if run['completion_status'] == 'complete' else 'RIP'
                    ])

class ItemEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Map Items")
        self.setMinimumWidth(400)
        self.items = []
        self.item_parser = ItemParser()
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
        dialog = ItemEntryDialog(self)
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