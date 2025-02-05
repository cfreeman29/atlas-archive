import sqlite3
import csv
from datetime import datetime
import json

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('poe2_maps.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                class TEXT NOT NULL,
                ascendancy TEXT
            )
        ''')
        
        # Create map_runs table with character_id foreign key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS map_runs (
                id INTEGER PRIMARY KEY,
                map_name TEXT,
                map_level INTEGER,
                boss_count INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                duration INTEGER,
                items TEXT,
                value REAL,
                completion_status TEXT DEFAULT 'complete',
                has_breach BOOLEAN DEFAULT 0,
                has_delirium BOOLEAN DEFAULT 0,
                has_expedition BOOLEAN DEFAULT 0,
                has_ritual BOOLEAN DEFAULT 0,
                breach_count INTEGER DEFAULT 0,
                character_id INTEGER,
                FOREIGN KEY (character_id) REFERENCES characters (id)
            )
        ''')
        self.conn.commit()
        
    def add_map_run(self, map_name, map_level, boss_count, start_time, duration, items, completion_status='complete',
                    has_breach=False, has_delirium=False, has_expedition=False, has_ritual=False, breach_count=0, character_id=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO map_runs (
                map_name, map_level, boss_count, start_time, duration, items, value, completion_status,
                has_breach, has_delirium, has_expedition, has_ritual, breach_count, character_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (map_name, map_level, boss_count, start_time, duration, json.dumps(items), 0, completion_status,
              has_breach, has_delirium, has_expedition, has_ritual, breach_count, character_id))
        self.conn.commit()
        
    def add_items_to_map(self, map_id, items):
        cursor = self.conn.cursor()
        cursor.execute('SELECT items FROM map_runs WHERE id = ?', (map_id,))
        result = cursor.fetchone()
        if result:
            existing_items = json.loads(result[0]) if result[0] else []
            # Combine items by name
            items_dict = {}
            
            # Process existing items
            for item in existing_items:
                name = item.get('name', 'Unknown')
                if (name != 'Unknown Item' and 
                    not name.startswith('Item Class:') and 
                    not name.startswith('Stack Size:') and 
                    not name.startswith('Rarity:')):
                    if name in items_dict:
                        items_dict[name]['stack_size'] += item.get('stack_size', 1)
                    else:
                        items_dict[name] = {
                            'name': name,
                            'stack_size': item.get('stack_size', 1),
                            'rarity': item.get('rarity'),
                            'item_class': item.get('item_class')
                        }
            
            # Add new items, combining if they already exist
            for item in items:
                name = item.get('name', 'Unknown')
                if (name != 'Unknown Item' and 
                    not name.startswith('Item Class:') and 
                    not name.startswith('Stack Size:') and 
                    not name.startswith('Rarity:')):
                    if name in items_dict:
                        items_dict[name]['stack_size'] += item.get('stack_size', 1)
                    else:
                        items_dict[name] = {
                            'name': name,
                            'stack_size': item.get('stack_size', 1),
                            'rarity': item.get('rarity'),
                            'item_class': item.get('item_class')
                        }
            
            # Convert back to list and save
            combined_items = list(items_dict.values())
            cursor.execute('UPDATE map_runs SET items = ? WHERE id = ?',
                         (json.dumps(combined_items), map_id))
            self.conn.commit()
            
    def add_items_to_latest_map(self, items):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM map_runs ORDER BY start_time DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            self.add_items_to_map(result[0], items)
            
    def delete_map_run(self, map_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM map_runs WHERE id = ?', (map_id,))
        self.conn.commit()
        
    def get_map_runs(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM map_runs ORDER BY start_time DESC')
        columns = [description[0] for description in cursor.description]
        runs = []
        for row in cursor.fetchall():
            run = dict(zip(columns, row))
            run['items'] = json.loads(run['items']) if run['items'] else []
            runs.append(run)
        return runs
        
    def clear_database(self):
        """Clear all records from the database."""
        cursor = self.conn.cursor()
        # Delete map runs first due to foreign key constraint
        cursor.execute('DELETE FROM map_runs')
        cursor.execute('DELETE FROM characters')
        self.conn.commit()
        
    def export_to_csv(self, file_path):
        """Export all data to CSV files"""
        cursor = self.conn.cursor()
        
        # Export characters
        with open(file_path.replace('.csv', '_characters.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Level', 'Class', 'Ascendancy'])
            cursor.execute('SELECT * FROM characters ORDER BY id')
            writer.writerows(cursor.fetchall())
        
        # Export map runs
        with open(file_path.replace('.csv', '_maps.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Map Name', 'Map Level', 'Boss Count', 'Start Time', 'Duration',
                'Items', 'Status', 'Has Breach', 'Has Delirium', 'Has Expedition',
                'Has Ritual', 'Breach Count', 'Character ID'
            ])
            
            cursor.execute('SELECT * FROM map_runs ORDER BY start_time')
            for row in cursor.fetchall():
                # Format duration as MM:SS
                duration_mins = row[5] // 60
                duration_secs = row[5] % 60
                duration_str = f"{duration_mins:02d}:{duration_secs:02d}"
                
                # Format items list
                items = json.loads(row[6]) if row[6] else []
                items_str = ", ".join(
                    f"{item['name']} x{item['stack_size']}"
                    for item in items
                    if item['name'] != 'Unknown Item'
                    and not item['name'].startswith('Item Class:')
                    and not item['name'].startswith('Stack Size:')
                    and not item['name'].startswith('Rarity:')
                ) or "None"
                
                writer.writerow([
                    row[0],  # ID
                    row[1],  # Map Name
                    row[2],  # Map Level
                    row[3],  # Boss Count
                    row[4],  # Start Time
                    duration_str,
                    items_str,
                    'Complete' if row[8] == 'complete' else 'RIP',
                    'Yes' if row[9] else 'No',  # Has Breach
                    'Yes' if row[10] else 'No',  # Has Delirium
                    'Yes' if row[11] else 'No',  # Has Expedition
                    'Yes' if row[12] else 'No',  # Has Ritual
                    row[13],  # Breach Count
                    row[14]   # Character ID
                ])
    
    def import_from_csv(self, characters_file, maps_file):
        """Import data from CSV files"""
        cursor = self.conn.cursor()
        
        # Import characters first
        with open(characters_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute('''
                    INSERT INTO characters (id, name, level, class, ascendancy)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    int(row['ID']),
                    row['Name'],
                    int(row['Level']),
                    row['Class'],
                    row['Ascendancy'] if row['Ascendancy'] != '' else None
                ))
        
        # Then import map runs
        with open(maps_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse duration from MM:SS format
                duration_parts = row['Duration'].split(':')
                duration = int(duration_parts[0]) * 60 + int(duration_parts[1])
                
                # Parse items from comma-separated string
                items = []
                if row['Items'] != 'None':
                    for item_str in row['Items'].split(', '):
                        if ' x' in item_str:
                            name, count = item_str.rsplit(' x', 1)
                            items.append({
                                'name': name,
                                'stack_size': int(count),
                                'rarity': None,
                                'item_class': None
                            })
                
                cursor.execute('''
                    INSERT INTO map_runs (
                        id, map_name, map_level, boss_count, start_time, duration, 
                        items, completion_status, has_breach, has_delirium,
                        has_expedition, has_ritual, breach_count, character_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    int(row['ID']),
                    row['Map Name'],
                    int(row['Map Level']),
                    int(row['Boss Count']),
                    row['Start Time'],
                    duration,
                    json.dumps(items),
                    'complete' if row['Status'] == 'Complete' else 'rip',
                    row['Has Breach'] == 'Yes',
                    row['Has Delirium'] == 'Yes',
                    row['Has Expedition'] == 'Yes',
                    row['Has Ritual'] == 'Yes',
                    int(row['Breach Count']),
                    int(row['Character ID']) if row['Character ID'] else None
                ))
        
        self.conn.commit()
        
    def add_character(self, name, character_class, level=1, ascendancy=None):
        """Add a new character to the database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO characters (name, class, level, ascendancy)
            VALUES (?, ?, ?, ?)
        ''', (name, character_class, level, ascendancy))
        self.conn.commit()
        return cursor.lastrowid
        
    def get_characters(self):
        """Get all characters"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM characters ORDER BY name')
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def get_character(self, character_id):
        """Get a specific character by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None
        
    def update_character(self, character_id, name=None, level=None, ascendancy=None):
        """Update a character's details"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if level is not None:
            updates.append("level = ?")
            params.append(level)
        if ascendancy is not None:
            updates.append("ascendancy = ?")
            params.append(ascendancy)
            
        if updates:
            query = f"UPDATE characters SET {', '.join(updates)} WHERE id = ?"
            params.append(character_id)
            cursor.execute(query, params)
            self.conn.commit()
        
    def get_character_runs(self, character_id):
        """Get all map runs for a specific character"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM map_runs WHERE character_id = ? ORDER BY start_time DESC', (character_id,))
        columns = [description[0] for description in cursor.description]
        runs = []
        for row in cursor.fetchall():
            run = dict(zip(columns, row))
            run['items'] = json.loads(run['items']) if run['items'] else []
            runs.append(run)
        return runs
