import re
from datetime import datetime
from pathlib import Path
import time

class LogParser:
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
        if current_size < self.last_position:
            # Log file was rotated
            self.last_position = 0
            
        if current_size == self.last_position:
            return []
            
        events = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            f.seek(self.last_position)
            for line in f:
                if "Generating level" in line:
                    match = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*"([\w_]+)" with seed (\d+)', line)
                    if match:
                        timestamp = datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
                        area_name = match.group(2)
                        seed = int(match.group(3))
                        
                        # Track the current area being generated
                        if area_name.startswith('Delirium'):
                            # Extract level from the original line
                            level_match = re.search(r'level (\d+) area', line)
                            level = level_match.group(1) if level_match else '??'
                            map_name = f'Simulacrum {level}'
                            has_boss = True  # Simulacrums always have bosses
                            
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'has_boss': has_boss,
                                'seed': seed
                            })
                        elif area_name.startswith('BreachDomain'):
                            # Extract level from the original line
                            level_match = re.search(r'level (\d+) area', line)
                            level = level_match.group(1) if level_match else '??'
                            map_name = f'Twisted Domain {level}'
                            has_boss = True  # Breach domains always have bosses
                            
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'has_boss': has_boss,
                                'seed': seed
                            })
                        elif area_name.startswith('Map'):
                            # Extract map name and boss status
                            # Format is "Map<name>_NoBoss" or "Map<name>"
                            map_parts = area_name.split('_')
                            # Remove "Map" prefix and add spaces before capital letters (except first letter)
                            raw_name = map_parts[0][3:]  # Remove "Map" prefix
                            map_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', raw_name)
                            has_boss = not (len(map_parts) > 1 and map_parts[1] == 'NoBoss')
                            
                            # Extract level from the original line
                            level_match = re.search(r'level (\d+) area', line)
                            area_level = int(level_match.group(1)) if level_match else 0
                            
                            # Map start event
                            events.append({
                                'type': 'map_start',
                                'timestamp': timestamp,
                                'map_name': map_name,
                                'has_boss': has_boss,
                                'seed': seed,
                                'area_level': area_level
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
