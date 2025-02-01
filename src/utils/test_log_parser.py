import unittest
import re
from pathlib import Path
from datetime import datetime
import sys
import time
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.log_parser import LogParser

class TestLogParser(unittest.TestCase):
    def setUp(self):
        # Create an empty temporary test log file
        self.test_log_path = Path("test_client.txt")
        self.test_log_path.touch()
        self.log_parser = LogParser(str(self.test_log_path))
        
    def tearDown(self):
        # Clean up the test log file
        if self.test_log_path.exists():
            self.test_log_path.unlink()
            
    def test_parse_map_start_with_boss(self):
        # Test parsing a map start event with a boss
        log_line = '2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 65 area "MapHiddenGrotto" with seed 1681684543\n'
        with open(self.test_log_path, 'w', encoding='utf-8') as f:
            f.write(log_line)
            
        events = self.log_parser.check_updates()
        self.assertEqual(len(events), 1)
        event = events[0]
        
        self.assertEqual(event['type'], 'map_start')
        self.assertEqual(event['map_name'], 'Hidden Grotto')
        self.assertEqual(event['map_level'], 65)
        self.assertTrue(event['has_boss'])
        self.assertEqual(event['seed'], 1681684543)
        self.assertEqual(event['timestamp'], datetime(2025, 1, 30, 18, 3, 45))
        
    def test_parse_map_start_no_boss(self):
        # Test parsing a map start event without a boss (with _NoBoss suffix)
        log_line = '2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 70 area "MapHiddenGrotto_NoBoss" with seed 1681684543\n'
        with open(self.test_log_path, 'w', encoding='utf-8') as f:
            f.write(log_line)
            
        events = self.log_parser.check_updates()
        self.assertEqual(len(events), 1)
        event = events[0]
        
        self.assertEqual(event['type'], 'map_start')
        self.assertEqual(event['map_name'], 'Hidden Grotto')
        self.assertEqual(event['map_level'], 70)
        self.assertFalse(event['has_boss'])
        self.assertEqual(event['seed'], 1681684543)
        
    def test_special_maps_no_boss(self):
        # Test maps that never have bosses even without _NoBoss suffix
        special_maps = [
            ('Lost Tower (Tower)', 'MapLostTower'),
            ('Mesa (Tower)', 'MapMesa'),
            ('Bluff (Tower)', 'MapBluff'),
            ('Sinking Spire (Tower)', 'MapSinkingSpire'),
            ('Alpine Ridge (Tower)', 'MapAlpineRidge')
        ]
        
        for display_name, map_name in special_maps:
            # Reset the file and parser for each test
            self.test_log_path.touch()
            self.log_parser = LogParser(str(self.test_log_path))
            
            # Write test content
            with open(self.test_log_path, 'a', encoding='utf-8') as f:
                f.write(f'2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 70 area "{map_name}" with seed 1681684543\n')
                
            events = self.log_parser.check_updates()
            self.assertEqual(len(events), 1, f"Failed to parse events for {display_name}")
            event = events[0]
            
            self.assertEqual(event['type'], 'map_start')
            self.assertEqual(event['map_name'], display_name)
            self.assertEqual(event['map_level'], 70)
            self.assertFalse(event['has_boss'], f"{display_name} should not have a boss")
            self.assertEqual(event['seed'], 1681684543)
        
    def test_parse_map_end(self):
        # Test parsing a map end event (entering non-map area)
        log_line = '2025/01/30 18:10:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 1 area "Hideout" with seed 1681684544\n'
        with open(self.test_log_path, 'w', encoding='utf-8') as f:
            f.write(log_line)
            
        events = self.log_parser.check_updates()
        self.assertEqual(len(events), 1)
        event = events[0]
        
        self.assertEqual(event['type'], 'map_end')
        self.assertEqual(event['next_area'], 'Hideout')
        self.assertEqual(event['timestamp'], datetime(2025, 1, 30, 18, 10, 45))
        
    def test_multiple_events(self):
        # Test parsing multiple events in sequence
        log_lines = [
            '2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 65 area "MapHiddenGrotto" with seed 1681684543\n',
            '2025/01/30 18:10:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 1 area "Hideout" with seed 1681684544\n',
            '2025/01/30 18:15:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 75 area "MapCrimsonTemple_NoBoss" with seed 1681684545\n'
        ]
        
        with open(self.test_log_path, 'w', encoding='utf-8') as f:
            f.writelines(log_lines)
            
        events = self.log_parser.check_updates()
        self.assertEqual(len(events), 3)
        
        # First event - Map start with boss
        self.assertEqual(events[0]['type'], 'map_start')
        self.assertEqual(events[0]['map_name'], 'Hidden Grotto')
        self.assertEqual(events[0]['map_level'], 65)
        self.assertTrue(events[0]['has_boss'])
        
        # Second event - Map end (hideout)
        self.assertEqual(events[1]['type'], 'map_end')
        self.assertEqual(events[1]['next_area'], 'Hideout')
        
        # Third event - Map start without boss
        self.assertEqual(events[2]['type'], 'map_start')
        self.assertEqual(events[2]['map_name'], 'Crimson Temple')
        self.assertEqual(events[2]['map_level'], 75)
        self.assertFalse(events[2]['has_boss'])
        
    def test_special_map_names(self):
        # Test special map name transformations for Breach and Delirium
        test_cases = [
            # Breach domain should be renamed to "Twisted Domain"
            ('2025/01/25 12:50:39 393591640 2caa1679 [DEBUG Client 44516] Generating level 80 area "BreachDomain_01" with seed 4160378910\n',
             'Twisted Domain'),
            # Delirium areas should be renamed to "Simulacrum"
            ('2025/01/26 03:04:56 444849093 2caa1679 [DEBUG Client 44516] Generating level 80 area "Delirium_Act1Town" with seed 3401619718\n',
             'Simulacrum'),
            # UberBoss maps should use the second part of the name
            ('2025/01/30 21:55:41 17718828 2caa1679 [DEBUG Client 5812] Generating level 85 area "MapUberBoss_CopperCitadel" with seed 1643808197\n',
             'Copper Citadel'),
            ('2025/01/30 22:15:36 18914015 2caa1679 [DEBUG Client 5812] Generating level 80 area "MapUberBoss_Monolith" with seed 1303021081\n',
             'Monolith'),
            ('2025/01/31 00:37:18 27415640 2caa1679 [DEBUG Client 5812] Generating level 72 area "MapUberBoss_IronCitadel" with seed 3497242900\n',
             'Iron Citadel'),
            ('2025/01/17 00:04:50 441419875 2caa1679 [DEBUG Client 86976] Generating level 79 area "MapUberBoss_StoneCitadel" with seed 3037379025\n',
             'Stone Citadel')
        ]
        
        for log_line, expected_name in test_cases:
            # Reset the file and parser for each test
            self.test_log_path.touch()
            self.log_parser = LogParser(str(self.test_log_path))
            self.log_parser.last_position = 0  # Explicitly reset position
            
            with open(self.test_log_path, 'w', encoding='utf-8') as f:
                f.write(log_line)
            
            # Debug: Print file contents and parser state
            print(f"\nTesting {expected_name}:")
            with open(self.test_log_path, 'r', encoding='utf-8') as f:
                print(f"File contents:\n{f.read()}")
            print(f"Parser position: {self.log_parser.last_position}")
                
            events = self.log_parser.check_updates()
            print(f"Events: {events}")
            self.assertEqual(len(events), 1, f"Failed to parse event for {expected_name}")
            event = events[0]
            
            self.assertEqual(event['type'], 'map_start')
            self.assertEqual(event['map_name'], expected_name, f"Expected map name to be {expected_name}")
            
            # Extract level from the log line to verify
            level_match = re.search(r'level (\d+)', log_line)
            expected_level = int(level_match.group(1))
            self.assertEqual(event['map_level'], expected_level, f"Expected level to be {expected_level}")
            
    def test_log_rotation(self):
        # Test handling of log file rotation
        # File is already created empty and parser is monitoring it from setUp()
        
        # Check initial state - should be no events
        events = self.log_parser.check_updates()
        self.assertEqual(len(events), 0)
        
        # Write first content
        with open(self.test_log_path, 'a', encoding='utf-8') as f:
            f.write('2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 65 area "MapHiddenGrotto" with seed 1681684543\n')
        
        print(f"\nAfter first write:")
        print(f"File size: {self.test_log_path.stat().st_size}")
        print(f"Parser position: {self.log_parser.last_position}")
        
        # Check for new events
        events = self.log_parser.check_updates()
        print(f"\nAfter first check:")
        print(f"File size: {self.test_log_path.stat().st_size}")
        print(f"Parser position: {self.log_parser.last_position}")
        print(f"Events: {events}")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['map_name'], 'Hidden Grotto')
        self.assertEqual(events[0]['map_level'], 65)
        
        # Write second content (simulating rotation)
        with open(self.test_log_path, 'a', encoding='utf-8') as f:
            f.write('2025/01/30 18:15:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 75 area "MapCrimsonTemple" with seed 1681684545\n')
        
        print(f"\nAfter second write:")
        print(f"File size: {self.test_log_path.stat().st_size}")
        print(f"Parser position: {self.log_parser.last_position}")
        
        events = self.log_parser.check_updates()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['map_name'], 'Crimson Temple')
        self.assertEqual(events[0]['map_level'], 75)

if __name__ == '__main__':
    unittest.main()
