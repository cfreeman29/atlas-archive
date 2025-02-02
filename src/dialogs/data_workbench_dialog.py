from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QComboBox, QTableWidget, QTableWidgetItem, QTabWidget,
                           QWidget)
from PyQt6.QtCore import Qt
import json
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DataWorkbenchDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Data Analysis Workbench")
        self.setMinimumSize(1000, 800)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Currency Analysis Tab
        currency_tab = QWidget()
        currency_layout = QVBoxLayout(currency_tab)
        
        # Currency correlation controls
        controls_layout = QHBoxLayout()
        
        # Map name filter
        self.map_filter_combo = QComboBox()
        self.map_filter_combo.addItem('All Maps')
        self.map_filter_combo.currentIndexChanged.connect(self.update_currency_analysis)
        controls_layout.addWidget(QLabel("Map Name:"))
        controls_layout.addWidget(self.map_filter_combo)

        # Map level filter
        self.level_filter_combo = QComboBox()
        self.level_filter_combo.addItem('All Levels')
        self.level_filter_combo.currentIndexChanged.connect(self.update_currency_analysis)
        controls_layout.addWidget(QLabel("Map Level:"))
        controls_layout.addWidget(self.level_filter_combo)

        # Mechanic filter
        self.mechanic_filter_combo = QComboBox()
        self.mechanic_filter_combo.addItems(['All Mechanics', 'With Breach', 'With Delirium', 'With Expedition', 'With Ritual'])
        self.mechanic_filter_combo.currentIndexChanged.connect(self.update_currency_analysis)
        controls_layout.addWidget(QLabel("Mechanic:"))
        controls_layout.addWidget(self.mechanic_filter_combo)

        # Currency type filter
        self.currency_type_combo = QComboBox()
        self.currency_type_combo.currentIndexChanged.connect(self.update_currency_analysis)
        controls_layout.addWidget(QLabel("Currency Type:"))
        controls_layout.addWidget(self.currency_type_combo)
        
        controls_layout.addStretch()
        currency_layout.addLayout(controls_layout)
        
        # Matplotlib figure for currency analysis
        self.currency_figure = Figure(figsize=(8, 6))
        self.currency_canvas = FigureCanvas(self.currency_figure)
        currency_layout.addWidget(self.currency_canvas)
        
        self.tab_widget.addTab(currency_tab, "Currency Analysis")
        
        # Mechanic Analysis Tab
        mechanic_tab = QWidget()
        mechanic_layout = QVBoxLayout(mechanic_tab)
        
        # Mechanic correlation controls
        mech_controls_layout = QHBoxLayout()
        
        self.mechanic_combo = QComboBox()
        self.mechanic_combo.addItems(['Breach', 'Delirium', 'Expedition', 'Ritual'])
        self.mechanic_combo.currentIndexChanged.connect(self.update_mechanic_analysis)
        mech_controls_layout.addWidget(QLabel("Mechanic:"))
        mech_controls_layout.addWidget(self.mechanic_combo)
        
        mech_controls_layout.addStretch()
        mechanic_layout.addLayout(mech_controls_layout)
        
        # Matplotlib figure for mechanic analysis
        self.mechanic_figure = Figure(figsize=(8, 6))
        self.mechanic_canvas = FigureCanvas(self.mechanic_figure)
        mechanic_layout.addWidget(self.mechanic_canvas)
        
        self.tab_widget.addTab(mechanic_tab, "Mechanic Analysis")
        
        # Raw Data Tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        self.data_table = QTableWidget()
        data_layout.addWidget(self.data_table)
        
        self.tab_widget.addTab(data_tab, "Raw Data")
        
        layout.addWidget(self.tab_widget)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #3d3d3d;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                gridline-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 5px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
    def load_data(self):
        runs = self.db.get_map_runs()
        self.df = pd.DataFrame(runs)
        
        # No need to process items data as it's already in list format from the database
        
        # Extract unique map levels, names, and currency types
        map_levels = sorted(self.df['map_level'].unique())
        self.level_filter_combo.addItems([str(level) for level in map_levels])

        map_names = sorted(self.df['map_name'].unique())
        self.map_filter_combo.addItems(map_names)

        currency_types = set()
        for items in self.df['items']:
            for item in items:
                if isinstance(item, dict) and item.get('name', '').endswith('_Currency'):
                    currency_types.add(item['name'].replace('_Currency', ''))
        
        self.currency_type_combo.addItems(sorted(currency_types))
        
        # Update visualizations
        self.update_currency_analysis()
        self.update_mechanic_analysis()
        self.update_raw_data_table()
        
    def get_currency_count(self, items, currency_type):
        count = 0
        for item in items:
            if isinstance(item, dict) and item.get('name') == f"{currency_type}_Currency":
                count += item.get('stack_size', 0)
        return count
        
    def update_currency_analysis(self):
        currency_type = self.currency_type_combo.currentText()
        mechanic_filter = self.mechanic_filter_combo.currentText()
        
        if not currency_type:
            return
            
        # Filter data based on selections
        filtered_df = self.df.copy()

        # Apply mechanic filter
        if mechanic_filter == 'With Breach':
            filtered_df = filtered_df[filtered_df['has_breach'] == 1]
        elif mechanic_filter == 'With Delirium':
            filtered_df = filtered_df[filtered_df['has_delirium'] == 1]
        elif mechanic_filter == 'With Expedition':
            filtered_df = filtered_df[filtered_df['has_expedition'] == 1]
        elif mechanic_filter == 'With Ritual':
            filtered_df = filtered_df[filtered_df['has_ritual'] == 1]

        # Apply map level filter
        level_filter = self.level_filter_combo.currentText()
        if level_filter != 'All Levels':
            filtered_df = filtered_df[filtered_df['map_level'] == int(level_filter)]

        # Apply map name filter
        map_filter = self.map_filter_combo.currentText()
        if map_filter != 'All Maps':
            filtered_df = filtered_df[filtered_df['map_name'] == map_filter]
            
        # Calculate currency counts
        filtered_df['currency_count'] = filtered_df['items'].apply(
            lambda items: self.get_currency_count(items, currency_type)
        )
        
        # Clear the figure
        self.currency_figure.clear()
        ax = self.currency_figure.add_subplot(111)
        
        if len(filtered_df) > 0:
            # Reset index to get sequential numbers for x-axis
            filtered_df = filtered_df.reset_index(drop=True)
            
            # Create scatter plot with hover annotations
            scatter = ax.scatter(filtered_df.index, filtered_df['currency_count'], alpha=0.6, picker=True)
            
            # Create annotation (initially hidden)
            annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                              bbox=dict(boxstyle="round,pad=0.5", fc="#1a1a1a", ec="gray", alpha=0.8),
                              color='white')
            annot.set_visible(False)
            
            def update_annot(ind):
                pos = scatter.get_offsets()[ind["ind"][0]]
                annot.xy = pos
                
                # Get the map run data for this point
                run_idx = ind["ind"][0]
                run = filtered_df.iloc[run_idx]
                
                # Format mechanics text
                mechanics = []
                if run['has_breach']:
                    mechanics.append(f"Breach ({run['breach_count']})")
                if run['has_delirium']:
                    mechanics.append("Delirium")
                if run['has_expedition']:
                    mechanics.append("Expedition")
                if run['has_ritual']:
                    mechanics.append("Ritual")
                mechanics_text = ", ".join(mechanics) if mechanics else "None"
                
                # Format duration
                duration_mins = run['duration'] // 60
                duration_secs = run['duration'] % 60
                
                # Create data plate text
                text = (f"Map: {run['map_name']} (Level {run['map_level']})\n"
                       f"Duration: {duration_mins:02d}:{duration_secs:02d}\n"
                       f"Mechanics: {mechanics_text}\n"
                       f"{currency_type}: {run['currency_count']}")
                
                annot.set_text(text)
            
            def hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    cont, ind = scatter.contains(event)
                    if cont:
                        update_annot(ind)
                        annot.set_visible(True)
                        self.currency_canvas.draw_idle()
                    elif vis:
                        annot.set_visible(False)
                        self.currency_canvas.draw_idle()
            
            self.currency_canvas.mpl_connect("motion_notify_event", hover)
            ax.set_xlabel('Map Run Number')
            ax.set_ylabel(f'{currency_type} Count')
            title = f'{currency_type} per Map Run'
            filters = []
            if mechanic_filter != 'All Mechanics':
                filters.append(mechanic_filter)
            if level_filter != 'All Levels':
                filters.append(f'Level {level_filter}')
            if map_filter != 'All Maps':
                filters.append(map_filter)
            if filters:
                title += f' ({" - ".join(filters)})'
            ax.set_title(title)
            
            # Add trend line if we have more than 1 point
            if len(filtered_df) > 1:
                try:
                    z = np.polyfit(filtered_df.index, filtered_df['currency_count'], 1)
                    p = np.poly1d(z)
                    ax.plot(filtered_df.index, p(filtered_df.index), "r--", alpha=0.8)
                except (TypeError, np.RankWarning):
                    # Skip trend line if fit fails
                    pass
            
            # Calculate and display average
            avg = filtered_df['currency_count'].mean()
            ax.axhline(y=avg, color='g', linestyle='--', alpha=0.5)
            ax.text(0.02, 0.98, f'Average: {avg:.2f}', 
                    transform=ax.transAxes, verticalalignment='top')
        else:
            ax.text(0.5, 0.5, 'No data available for selected filter',
                   horizontalalignment='center',
                   verticalalignment='center',
                   color='white')
        
        # Style the plot
        ax.set_facecolor('#2d2d2d')
        self.currency_figure.patch.set_facecolor('#1a1a1a')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        
        self.currency_canvas.draw()
        
    def update_mechanic_analysis(self):
        mechanic = self.mechanic_combo.currentText().lower()
        
        # Clear the figure
        self.mechanic_figure.clear()
        ax = self.mechanic_figure.add_subplot(111)
        
        # Calculate relevant metrics
        mechanic_runs = self.df[self.df[f'has_{mechanic}'] == 1]
        non_mechanic_runs = self.df[self.df[f'has_{mechanic}'] == 0]
        
        # Prepare data for box plots
        data = []
        labels = []
        
        # Add duration comparison
        if len(mechanic_runs) > 0:
            data.append(mechanic_runs['duration'] / 60)  # Convert to minutes
            labels.append(f'With {mechanic.capitalize()}')
        if len(non_mechanic_runs) > 0:
            data.append(non_mechanic_runs['duration'] / 60)
            labels.append(f'Without {mechanic.capitalize()}')
            
        if data:
            # Create box plot
            ax.boxplot(data, labels=labels)
            ax.set_ylabel('Duration (minutes)')
            ax.set_title(f'Map Duration Comparison - {mechanic.capitalize()}')
            
            # Add average values
            if len(mechanic_runs) > 0:
                avg_with = mechanic_runs['duration'].mean() / 60
                ax.text(1, ax.get_ylim()[1], f'Avg: {avg_with:.1f}m', 
                       horizontalalignment='center', verticalalignment='bottom')
            if len(non_mechanic_runs) > 0:
                avg_without = non_mechanic_runs['duration'].mean() / 60
                ax.text(2, ax.get_ylim()[1], f'Avg: {avg_without:.1f}m',
                       horizontalalignment='center', verticalalignment='bottom')
        else:
            ax.text(0.5, 0.5, 'No data available for selected mechanic',
                   horizontalalignment='center',
                   verticalalignment='center',
                   color='white')
        
        # Style the plot
        ax.set_facecolor('#2d2d2d')
        self.mechanic_figure.patch.set_facecolor('#1a1a1a')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        
        self.mechanic_canvas.draw()
        
    def update_raw_data_table(self):
        # Set up table columns
        columns = ['Map Name', 'Level', 'Duration', 'Mechanics', 'Currency Found']
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        
        # Populate table
        self.data_table.setRowCount(len(self.df))
        for i, (_, run) in enumerate(self.df.iterrows()):
            # Map name and level
            self.data_table.setItem(i, 0, QTableWidgetItem(run['map_name']))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(run['map_level'])))
            
            # Duration
            mins = run['duration'] // 60
            secs = run['duration'] % 60
            self.data_table.setItem(i, 2, QTableWidgetItem(f"{mins:02d}:{secs:02d}"))
            
            # Mechanics
            mechanics = []
            if run['has_breach']:
                mechanics.append(f"Breach ({run['breach_count']})")
            if run['has_delirium']:
                mechanics.append("Delirium")
            if run['has_expedition']:
                mechanics.append("Expedition")
            if run['has_ritual']:
                mechanics.append("Ritual")
            self.data_table.setItem(i, 3, QTableWidgetItem(", ".join(mechanics)))
            
            # Currency summary
            currency_summary = []
            for item in run['items']:
                if isinstance(item, dict) and item.get('name', '').endswith('_Currency'):
                    name = item['name'].replace('_Currency', '')
                    count = item.get('stack_size', 0)
                    currency_summary.append(f"{name} x{count}")
            self.data_table.setItem(i, 4, QTableWidgetItem(", ".join(currency_summary)))
            
        # Adjust column widths
        self.data_table.resizeColumnsToContents()
