import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('poe2_maps.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
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
                breach_count INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
        
    def add_map_run(self, map_name, map_level, boss_count, start_time, duration, items, completion_status='complete',
                    has_breach=False, has_delirium=False, has_expedition=False, has_ritual=False, breach_count=0):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO map_runs (
                map_name, map_level, boss_count, start_time, duration, items, value, completion_status,
                has_breach, has_delirium, has_expedition, has_ritual, breach_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (map_name, map_level, boss_count, start_time, duration, json.dumps(items), 0, completion_status,
              has_breach, has_delirium, has_expedition, has_ritual, breach_count))
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
