import csv
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QListWidget, QListWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt

from .map_run_details_dialog import MapRunDetailsDialog

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
        
        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_btn)
        
        # Import button
        import_btn = QPushButton("Import from CSV")
        import_btn.clicked.connect(self.import_from_csv)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        
        # Clear DB button (right-aligned)
        clear_btn = QPushButton("Clear Database")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: white;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        clear_btn.clicked.connect(self.clear_database)
        button_layout.addWidget(clear_btn)
        
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
        total_single_bosses = sum(1 for run in runs if run['boss_count'] == 1)
        total_twin_bosses = sum(1 for run in runs if run['boss_count'] == 2)
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
            boss_text = "No Boss"
            if run['boss_count'] == 1:
                boss_text = "Single Boss"
            elif run['boss_count'] == 2:
                boss_text = "Twin Boss"
                
            item_text = (f"{run['map_name']} (Level {run['map_level']}) - {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Duration: {duration_mins:02d}:{duration_secs:02d} | "
                        f"Boss: {boss_text} | "
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
            f"Single Bosses: {total_single_bosses} | Twin Bosses: {total_twin_bosses} | "
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
                writer.writerow(['ID', 'Map Name', 'Map Level', 'Boss Count', 'Start Time', 'Duration', 'Items', 'Status'])
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
                        run['map_level'],
                        run['boss_count'],
                        run['start_time'],
                        f"{duration_mins:02d}:{duration_secs:02d}",
                        items_text if items_text else "None",
                        'Complete' if run['completion_status'] == 'complete' else 'RIP'
                    ])
                    
    def import_from_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import Map Runs",
            str(Path.home()),
            "CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.db.import_from_csv(reader)
                    self.load_runs()
                    QMessageBox.information(
                        self,
                        "Import Successful",
                        "Map runs have been imported successfully."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import map runs: {str(e)}"
                )
                
    def clear_database(self):
        reply = QMessageBox.question(
            self,
            "Clear Database",
            "Are you sure you want to clear all map run data? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_database()
            self.load_runs()
            QMessageBox.information(
                self,
                "Database Cleared",
                "All map run data has been cleared successfully."
            )
