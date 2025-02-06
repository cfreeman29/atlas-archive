import csv
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
                           QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ..utils.resource_path import get_resource_path

from .map_run_details_dialog import MapRunDetailsDialog
from .data_workbench_dialog import DataWorkbenchDialog

class MapRunsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Map Runs History")
        self.setMinimumSize(800, 600)
        self.active_filters = {
            'breach': False,
            'delirium': False,
            'expedition': False,
            'ritual': False
        }
        self.selected_character = None
        self.selected_build = None
        self.setup_ui()
        self.load_runs()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Top bar with stats, character filter, and mechanic filters
        top_bar = QHBoxLayout()
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 14px; color: #cccccc;")
        top_bar.addWidget(self.stats_label)
        
        # Add stretch to push filters to the right
        top_bar.addStretch()
        
        # Character and Build filters
        filter_layout = QHBoxLayout()
        
        # Character filter
        filter_layout.addWidget(QLabel("Character:"))
        self.char_combo = QComboBox()
        self.char_combo.addItem("All Characters", None)
        characters = self.db.get_characters()
        for char in characters:
            self.char_combo.addItem(
                f"{char['name']} (Level {char['level']} {char['class']}"
                f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''}",
                char['id']
            )
        self.char_combo.currentIndexChanged.connect(self.on_character_filter_changed)
        filter_layout.addWidget(self.char_combo)
        
        # Build filter
        filter_layout.addWidget(QLabel("Build:"))
        self.build_combo = QComboBox()
        self.build_combo.addItem("All Builds", None)
        self.build_combo.currentIndexChanged.connect(self.on_build_filter_changed)
        filter_layout.addWidget(self.build_combo)
        
        top_bar.addLayout(filter_layout)
        
        # Mechanic filter buttons
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        
        # Create filter buttons for each mechanic
        mechanics = ['breach', 'delirium', 'expedition', 'ritual']
        self.filter_buttons = {}
        
        for mech in mechanics:
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setCheckable(True)
            btn.setProperty('mechanic', mech)
            btn.clicked.connect(self.toggle_filter)
            
            # Set icons
            active_icon = QIcon(get_resource_path(f'src/images/endgame-mech/{mech}.png'))
            inactive_icon = QIcon(get_resource_path(f'src/images/endgame-mech/{mech}_off.png'))
            btn.setIcon(inactive_icon)
            btn.setProperty('active_icon', active_icon)
            btn.setProperty('inactive_icon', inactive_icon)
            btn.setIconSize(btn.size())
            
            filter_layout.addWidget(btn)
            self.filter_buttons[mech] = btn
            
        top_bar.addLayout(filter_layout)
        layout.addLayout(top_bar)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.show_run_details)
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Left side buttons
        left_buttons = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        left_buttons.addWidget(export_btn)
        
        # Import button
        import_btn = QPushButton("Import from CSV")
        import_btn.clicked.connect(self.import_from_csv)
        left_buttons.addWidget(import_btn)
        
        # Data Analysis button
        analyze_btn = QPushButton("Data Analysis")
        analyze_btn.clicked.connect(self.show_data_analysis)
        left_buttons.addWidget(analyze_btn)
        
        button_layout.addLayout(left_buttons)
        
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
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #4a4a4a;
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
            QPushButton[mechanic] {
                background-color: transparent;
                padding: 4px;
            }
            QPushButton[mechanic]:checked {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton[mechanic]:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        
    def update_build_filter(self):
        """Update build filter dropdown based on selected character"""
        self.build_combo.clear()
        self.build_combo.addItem("All Builds", None)
        
        if self.selected_character:
            builds = self.db.get_builds(self.selected_character)
            for build in builds:
                self.build_combo.addItem(build['name'], build['id'])
                
    def on_build_filter_changed(self, index):
        """Handle build filter selection"""
        self.selected_build = self.build_combo.currentData()
        self.load_runs()
        
    def on_character_filter_changed(self, index):
        """Handle character filter selection"""
        self.selected_character = self.char_combo.currentData()
        self.selected_build = None  # Reset build filter
        self.update_build_filter()  # Update build dropdown
        self.load_runs()
        
    def toggle_filter(self):
        btn = self.sender()
        mech = btn.property('mechanic')
        is_active = btn.isChecked()
        
        # Update filter state
        self.active_filters[mech] = is_active
        
        # Update button icon
        btn.setIcon(btn.property('active_icon') if is_active else btn.property('inactive_icon'))
        
        # Reload runs with new filters
        self.load_runs()
        
    def load_runs(self):
        all_runs = self.db.get_map_runs()
        
        # Filter runs based on active mechanic filters, selected character, and build
        runs = []
        for run in all_runs:
            include_run = True
            # Check mechanic filters
            for mech, active in self.active_filters.items():
                if active and not run[f'has_{mech}']:
                    include_run = False
                    break
            # Check character filter
            if self.selected_character is not None and run['character_id'] != self.selected_character:
                include_run = False
            # Check build filter
            if include_run and self.selected_build is not None:
                if run['build_id'] != self.selected_build:
                    include_run = False
            if include_run:
                runs.append(run)
                
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
            
            # Get character and build info if available
            character_info = ""
            build_info = ""
            if run['character_id']:
                char = self.db.get_character(run['character_id'])
                if char:
                    character_info = (f" | Character: {char['name']} "
                                    f"(Level {char['level']} {char['class']}"
                                    f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''})")
            if run['build_id']:
                build = self.db.get_build(run['build_id'])
                if build:
                    build_info = f" | Build: {build['name']} ({build['url']})"
            
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
                
            # Add mechanic indicators to the summary
            mechanics_text = []
            if run['has_breach']:
                mechanics_text.append(f"Breach ({run['breach_count']})")
            if run['has_delirium']:
                mechanics_text.append("Delirium")
            if run['has_expedition']:
                mechanics_text.append("Expedition")
            if run['has_ritual']:
                mechanics_text.append("Ritual")
            mechanics_str = f" | Mechanics: {', '.join(mechanics_text)}" if mechanics_text else ""
                
            item_text = (f"{run['map_name']} (Level {run['map_level']}) - {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Duration: {duration_mins:02d}:{duration_secs:02d} | "
                        f"Boss: {boss_text} | "
                        f"Items: {item_count} | "
                        f"Status: {'Complete' if run['completion_status'] == 'complete' else 'RIP'}"
                        f"{character_info}"
                        f"{mechanics_str}"
                        f"{build_info}")
            
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
            "Export Data",
            str(Path.home() / "atlas_archive_export.csv"),
            "CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                self.db.export_to_csv(file_name)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Data has been exported to:\n"
                    f"{file_name}\n"
                    f"{file_name.replace('.csv', '_characters.csv')}\n"
                    f"{file_name.replace('.csv', '_builds.csv')}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export data: {str(e)}"
                )
                    
    def import_from_csv(self):
        # Get characters file
        chars_file, _ = QFileDialog.getOpenFileName(
            self,
            "Import Characters CSV",
            str(Path.home()),
            "CSV Files (*_characters.csv)"
        )
        
        if not chars_file:
            return
            
        # Get maps file
        maps_file, _ = QFileDialog.getOpenFileName(
            self,
            "Import Maps CSV",
            str(Path.home()),
            "CSV Files (*_maps.csv)"
        )
        
        if not maps_file:
            return
            
        # Get builds file (optional)
        builds_file, _ = QFileDialog.getOpenFileName(
            self,
            "Import Builds CSV (Optional)",
            str(Path.home()),
            "CSV Files (*_builds.csv)"
        )
        
        try:
            self.db.import_from_csv(chars_file, maps_file, builds_file)
            self.load_runs()
            # Reset filters
            self.selected_character = None
            self.selected_build = None
            # Refresh character filter
            self.char_combo.clear()
            self.char_combo.addItem("All Characters", None)
            characters = self.db.get_characters()
            for char in characters:
                self.char_combo.addItem(
                    f"{char['name']} (Level {char['level']} {char['class']}"
                    f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''}",
                    char['id']
                )
            # Reset build filter
            self.build_combo.clear()
            self.build_combo.addItem("All Builds", None)
            QMessageBox.information(
                self,
                "Import Successful",
                "Data has been imported successfully."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import data: {str(e)}"
            )
                
    def clear_database(self):
        reply = QMessageBox.question(
            self,
            "Clear Database",
            "Are you sure you want to clear all data? This will remove all characters, builds, and map runs. This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_database()
            self.load_runs()
            # Refresh character filter
            self.char_combo.clear()
            self.char_combo.addItem("All Characters", None)
            # Clear build filter
            self.build_combo.clear()
            self.build_combo.addItem("All Builds", None)
            QMessageBox.information(
                self,
                "Database Cleared",
                "All data has been cleared successfully."
            )
            
    def show_data_analysis(self):
        dialog = DataWorkbenchDialog(self.db, self)
        dialog.exec()
