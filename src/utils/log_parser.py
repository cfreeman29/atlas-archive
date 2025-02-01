import re
from datetime import datetime
from pathlib import Path
import time

class LogParser:
    # Maps that never have bosses, even without _NoBoss suffix
    NO_BOSS_MAPS = {
        'MapLostTower',
        'MapMesa',
        'MapBluff',
        'MapSinkingSpire',
        'MapAlpineRidge'
    }
    
    def __init__(self, custom_path=None):
        if custom_path:
            self.log_path = Path(custom_path)
        else:
            self.log_path = Path.home() / "Documents" / "My Games" / "Path of Exile 2" / "logs" / "Client.txt"
        self.last_position = self.log_path.stat().st_size if self.log_path.exists() else 0
        
    def check_updates(self):
        if not self.log_path.exists():
            return []
            
        current_size = self.log_path.stat().st_size
        # Reset position if file is empty or rotated
        if current_size == 0 or current_size < self.last_position:
            self.last_position = 0
            
        if current_size == self.last_position:
            return []
            
        events = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            f.seek(self.last_position)
            for line in f:
                if "Generating level" in line:
                    print(f"Processing line: {line.strip()}")  # Debug print
                    match = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*level (\d+) area "([^"]+)" with seed (\d+)', line)
                    if match:
                        print(f"Match groups: {match.groups()}")  # Debug print
                    else:
                        print("No match found")  # Debug print
                    if match:
                        timestamp = datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
                        area_level = int(match.group(2))
                        area_name = match.group(3)
                        seed = int(match.group(4))
                        
                        # Handle special map names first
                        if area_name.startswith('MapUberBoss_'):
                            # Extract the second part after MapUberBoss_ and format it
                            raw_name = area_name[len('MapUberBoss_'):]
                            map_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', raw_name)
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'map_level': area_level,
                                'has_boss': True,
                                'seed': seed
                            })
                        elif area_name.startswith('Breach'):
                            # Breach domains should be renamed to "Twisted Domain"
                            map_name = "Twisted Domain"
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'map_level': area_level,
                                'has_boss': True,
                                'seed': seed
                            })
                        elif area_name.startswith('Delirium'):
                            # Delirium areas should be renamed to "Simulacrum"
                            map_name = "Simulacrum"
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'map_level': area_level,
                                'has_boss': True,
                                'seed': seed
                            })
                        # Handle regular map areas
                        elif area_name.startswith('Map'):
                            # Extract map name and boss status
                            # Format is "Map<name>_NoBoss" or "Map<name>"
                            map_parts = area_name.split('_')
                            # Remove "Map" prefix and add spaces before capital letters (except first letter)
                            raw_name = map_parts[0][3:]  # Remove "Map" prefix
                            map_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', raw_name)
                            
                            # Check for maps that never have bosses
                            is_tower_map = area_name in self.NO_BOSS_MAPS
                            has_boss = not (len(map_parts) > 1 and map_parts[1] == 'NoBoss' or is_tower_map)
                            
                            # Append (Tower) to special maps
                            if is_tower_map:
                                map_name = f"{map_name} (Tower)"
                            
                            # Map start event
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'map_level': area_level,
                                'has_boss': has_boss,
                                'seed': seed
                            })
                        else:
                            # Any non-map area counts as a map end event
                            events.append({
                                'type': 'map_end',
                                'timestamp': timestamp,
                                'next_area': area_name
                            })
                        
        self.last_position = current_size
        return events
