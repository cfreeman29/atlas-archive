import unittest
from .log_parser import LogParser
from pathlib import Path
import tempfile

class TestLogParser(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = Path(self.temp_dir) / "test_client.txt"
        self.parser = LogParser(str(self.temp_log))
        
    def test_breach_domain_parsing(self):
        # Test BreachDomain parsing
        with open(self.temp_log, 'w', encoding='utf-8') as f:
            f.write('2024/01/29 18:17:55 123456789 d0 [INFO Client 6512] Generating level 82 area "BreachDomain_01" with seed 799606985\n')
        
        # Reset parser position to ensure it reads from start
        self.parser.last_position = 0
        events = self.parser.check_updates()
        self.assertEqual(len(events), 1)
        event = events[0]
        
        self.assertEqual(event['type'], 'map_start')
        self.assertEqual(event['map_name'], 'Twisted Domain 82')
        self.assertTrue(event['has_boss'])
        self.assertEqual(event['seed'], 799606985)

    def test_delirium_parsing(self):
        # Test Delirium parsing
        with open(self.temp_log, 'w', encoding='utf-8') as f:
            f.write('2024/01/29 18:17:55 123456789 d0 [INFO Client 6512] Generating level 80 area "Delirium_Act1Town" with seed 3401619718\n')
        
        # Reset parser position to ensure it reads from start
        self.parser.last_position = 0
        events = self.parser.check_updates()
        self.assertEqual(len(events), 1)
        event = events[0]
        
        self.assertEqual(event['type'], 'map_start')
        self.assertEqual(event['map_name'], 'Simulacrum 80')
        self.assertTrue(event['has_boss'])
        self.assertEqual(event['seed'], 3401619718)

if __name__ == '__main__':
    unittest.main()
