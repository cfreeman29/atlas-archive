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
        
        # Character Analysis Tab
        character_tab = QWidget()
        character_layout = QVBoxLayout(character_tab)
        
        # Character selection controls
        char_controls_layout = QHBoxLayout()
        
        self.char_combo = QComboBox()
        self.char_combo.addItem('All Characters')
        self.char_combo.currentIndexChanged.connect(self.update_character_analysis)
        char_controls_layout.addWidget(QLabel("Character:"))
        char_controls_layout.addWidget(self.char_combo)
        
        char_controls_layout.addStretch()
        character_layout.addLayout(char_controls_layout)
        
        # Matplotlib figure for character analysis
        self.character_figure = Figure(figsize=(8, 6))
        self.character_canvas = FigureCanvas(self.character_figure)
        character_layout.addWidget(self.character_canvas)
        
        self.tab_widget.addTab(character_tab, "Character Analysis")
        
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
        # Load map runs
        runs = self.db.get_map_runs()
        self.df = pd.DataFrame(runs)
        
        # Load characters and add to combo box
        characters = self.db.get_characters()
        for char in characters:
            self.char_combo.addItem(
                f"{char['name']} (Level {char['level']} {char['class']}"
                f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''})",
                char['id']
            )
        
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
        self.update_character_analysis()
        self.update_currency_analysis()
        self.update_mechanic_analysis()
        self.update_raw_data_table()
        
    def update_character_analysis(self):
        # Clear the figure
        self.character_figure.clear()
        
        # Create subplots for different metrics
        gs = self.character_figure.add_gridspec(2, 2)
        ax1 = self.character_figure.add_subplot(gs[0, 0])  # Map completion rate
        ax2 = self.character_figure.add_subplot(gs[0, 1])  # Average duration
        ax3 = self.character_figure.add_subplot(gs[1, :])  # Map level progression
        
        # Get selected character
        char_id = self.char_combo.currentData()
        
        if char_id is not None:
            # Filter data for selected character
            char_df = self.df[self.df['character_id'] == char_id]
            
            if len(char_df) > 0:
                # Map completion rate pie chart
                complete = len(char_df[char_df['completion_status'] == 'complete'])
                rips = len(char_df[char_df['completion_status'] == 'rip'])
                ax1.pie([complete, rips], labels=['Complete', 'RIP'], colors=['#44ff44', '#ff4444'],
                       autopct='%1.1f%%')
                ax1.set_title('Map Completion Rate')
                
                # Average duration by map level
                avg_duration = char_df.groupby('map_level')['duration'].mean() / 60  # Convert to minutes
                ax2.bar(avg_duration.index, avg_duration.values)
                ax2.set_xlabel('Map Level')
                ax2.set_ylabel('Average Duration (minutes)')
                ax2.set_title('Average Map Duration by Level')
                
                # Map level progression over time
                ax3.plot(pd.to_datetime(char_df['start_time']), char_df['map_level'], marker='o')
                ax3.set_xlabel('Date')
                ax3.set_ylabel('Map Level')
                ax3.set_title('Map Level Progression')
                ax3.tick_params(axis='x', rotation=45)
                
                # Add summary text
                total_maps = len(char_df)
                avg_duration_all = char_df['duration'].mean() / 60
                ax3.text(0.02, 0.98, 
                        f'Total Maps: {total_maps}\n'
                        f'Average Duration: {avg_duration_all:.1f}m\n'
                        f'Highest Level: {char_df["map_level"].max()}',
                        transform=ax3.transAxes,
                        verticalalignment='top',
                        bbox=dict(facecolor='#1a1a1a', alpha=0.8))
            else:
                for ax in [ax1, ax2, ax3]:
                    ax.text(0.5, 0.5, 'No data available for selected character',
                           horizontalalignment='center',
                           verticalalignment='center',
                           color='white')
        else:
            # Compare all characters
            char_stats = []
            for char in self.db.get_characters():
                char_df = self.df[self.df['character_id'] == char['id']]
                if len(char_df) > 0:
                    stats = {
                        'name': char['name'],
                        'total_maps': len(char_df),
                        'completion_rate': len(char_df[char_df['completion_status'] == 'complete']) / len(char_df) * 100,
                        'avg_duration': char_df['duration'].mean() / 60,
                        'highest_level': char_df['map_level'].max()
                    }
                    char_stats.append(stats)
            
            if char_stats:
                char_df = pd.DataFrame(char_stats)
                
                # Completion rate comparison
                ax1.bar(char_df['name'], char_df['completion_rate'])
                ax1.set_xlabel('Character')
                ax1.set_ylabel('Completion Rate (%)')
                ax1.set_title('Map Completion Rate by Character')
                ax1.tick_params(axis='x', rotation=45)
                
                # Average duration comparison
                ax2.bar(char_df['name'], char_df['avg_duration'])
                ax2.set_xlabel('Character')
                ax2.set_ylabel('Average Duration (minutes)')
                ax2.set_title('Average Map Duration by Character')
                ax2.tick_params(axis='x', rotation=45)
                
                # Map level comparison
                ax3.bar(char_df['name'], char_df['highest_level'])
                ax3.set_xlabel('Character')
                ax3.set_ylabel('Highest Map Level')
                ax3.set_title('Highest Map Level by Character')
                ax3.tick_params(axis='x', rotation=45)
            else:
                for ax in [ax1, ax2, ax3]:
                    ax.text(0.5, 0.5, 'No map data available',
                           horizontalalignment='center',
                           verticalalignment='center',
                           color='white')
        
        # Style the plots
        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor('#2d2d2d')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
        
        self.character_figure.patch.set_facecolor('#1a1a1a')
        self.character_figure.tight_layout()
        self.character_canvas.draw()
        
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
                
                # Get character info
                char_info = ""
                if run['character_id']:
                    char = self.db.get_character(run['character_id'])
                    if char:
                        char_info = f"\nCharacter: {char['name']}"
                
                # Create data plate text
                text = (f"Map: {run['map_name']} (Level {run['map_level']})\n"
                       f"Duration: {duration_mins:02d}:{duration_secs:02d}\n"
                       f"Mechanics: {mechanics_text}\n"
                       f"{currency_type}: {run['currency_count']}"
                       f"{char_info}")
                
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
        columns = ['Map Name', 'Level', 'Duration', 'Character', 'Mechanics', 'Currency Found']
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
            
            # Character
            char_text = ""
            if run['character_id']:
                char = self.db.get_character(run['character_id'])
                if char:
                    char_text = (f"{char['name']} (Level {char['level']} {char['class']}"
                               f"{' - ' + char['ascendancy'] if char['ascendancy'] else ''})")
            self.data_table.setItem(i, 3, QTableWidgetItem(char_text))
            
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
            self.data_table.setItem(i, 4, QTableWidgetItem(", ".join(mechanics)))
            
            # Currency summary
            currency_summary = []
            for item in run['items']:
                if isinstance(item, dict) and item.get('name', '').endswith('_Currency'):
                    name = item['name'].replace('_Currency', '')
                    count = item.get('stack_size', 0)
                    currency_summary.append(f"{name} x{count}")
            self.data_table.setItem(i, 5, QTableWidgetItem(", ".join(currency_summary)))
            
        # Adjust column widths
        self.data_table.resizeColumnsToContents()
