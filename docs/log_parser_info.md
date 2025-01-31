# Log Parser Documentation

The log parser is responsible for monitoring and parsing the Path of Exile 2 Client.txt log file to track map runs. This document explains how the parser works and how to configure or modify it.

## Overview

The log parser (`src/utils/log_parser.py`) monitors the game's Client.txt file for specific log entries that indicate:
- Map start events (entering a new map)
- Map end events (leaving a map)

## Log File Format

The parser looks for lines matching this format:
```
YYYY/MM/DD HH:MM:SS [process_id] [hash] [DEBUG Client port] Generating level [level] area "[area_name]" with seed [seed]
```

Example:
```
2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 65 area "MapHiddenGrotto_NoBoss" with seed 1681684543
```

## Parsed Information

For each map event, the parser extracts:

### Map Start Events
- Timestamp
- Map name (cleaned up from the area name)
- Map level
- Boss status (has boss or no boss)
- Seed value

### Map End Events
- Timestamp
- Next area name

## Map Name Processing

Map names in the log follow these conventions:
1. Start with "Map" prefix
2. Use CamelCase for multi-word names
3. May have "_NoBoss" suffix

The parser:
1. Removes the "Map" prefix
2. Splits CamelCase into spaces
3. Checks for "_NoBoss" suffix to determine boss status

Example:
- Log name: "MapHiddenGrotto_NoBoss"
- Parsed name: "Hidden Grotto"
- Boss status: false

## Configuration

### Custom Log Path

By default, the parser looks for Client.txt in:
```
%USERPROFILE%/Documents/My Games/Path of Exile 2/logs/Client.txt
```

You can specify a custom path when initializing the parser:
```python
parser = LogParser(custom_path="path/to/client.txt")
```

### Log Rotation Handling

The parser automatically handles log rotation:
- If the file size becomes smaller than the last read position
- Resets to beginning of file
- Continues parsing from there

## Modifying the Parser

### Adding New Event Types

To track new types of log entries:

1. Add new regex pattern in `check_updates()`:
```python
if "Your Pattern" in line:
    match = re.search(r'your_regex_pattern', line)
    if match:
        # Extract information
        # Create event dictionary
        events.append({
            'type': 'your_event_type',
            'your_data': extracted_data
        })
```

2. Update tests in `test_log_parser.py`

### Modifying Map Name Processing

The map name processing is done in `check_updates()`. To modify how names are processed:

1. Find the map processing section:
```python
if area_name.startswith('Map'):
    map_parts = area_name.split('_')
    raw_name = map_parts[0][3:]  # Remove "Map" prefix
    map_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', raw_name)
```

2. Adjust the regex or string operations as needed

## Testing

The parser includes a comprehensive test suite in `test_log_parser.py`. This test suite simulates how the log parser works in a real environment by creating temporary log files and monitoring them for changes.

### Running Tests
```bash
python -m unittest src/utils/test_log_parser.py
```

### Test Structure

The test suite uses Python's unittest framework and includes several key test cases:

#### Setup and Teardown
- Each test creates a temporary log file (`test_client.txt`)
- The log parser is initialized to monitor this file
- After each test, the temporary file is cleaned up

#### Test Cases

1. `test_parse_map_start_with_boss`:
   - Tests parsing a map event with a boss
   - Verifies map name, level, boss status, and timestamp extraction
   - Example log line: `2025/01/30 18:03:45 ... Generating level 65 area "MapHiddenGrotto" with seed 1681684543`

2. `test_parse_map_start_no_boss`:
   - Tests parsing a map event without a boss
   - Verifies handling of "_NoBoss" suffix
   - Example log line: `... Generating level 70 area "MapHiddenGrotto_NoBoss" with seed 1681684543`

3. `test_parse_map_end`:
   - Tests detection of map end events (entering non-map areas)
   - Example log line: `... Generating level 1 area "Hideout" with seed 1681684544`

4. `test_multiple_events`:
   - Tests parsing multiple sequential events
   - Verifies correct ordering and parsing of multiple log lines
   - Tests combination of map starts and ends

5. `test_log_rotation`:
   - Simulates log file rotation scenario
   - Tests parser's ability to handle file truncation/rotation
   - Process:
     1. Creates empty file and starts monitoring
     2. Appends first log entry
     3. Verifies first entry is parsed
     4. Appends second entry
     5. Verifies second entry is parsed
   - This simulates how the actual game client writes to its log file

### Adding New Tests

When adding new functionality to the parser:

1. Create a new test method in `TestLogParser` class
2. Follow the pattern:
   ```python
   def test_new_feature(self):
       # Write test log content
       with open(self.test_log_path, 'w', encoding='utf-8') as f:
           f.write('your test log line\n')
       
       # Get and verify events
       events = self.log_parser.check_updates()
       self.assertEqual(len(events), expected_count)
       # Add assertions for event content
   ```

3. Ensure test method name starts with `test_`
4. Include clear comments explaining what's being tested
5. Use descriptive assertion messages

### Test Data

Test log lines should follow this format:
```
YYYY/MM/DD HH:MM:SS [process_id] [hash] [DEBUG Client port] Generating level [level] area "[area_name]" with seed [seed]
```

Example:
```
2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 65 area "MapHiddenGrotto" with seed 1681684543
```

When modifying the parser, ensure all tests pass and add new tests for new functionality. The test suite helps ensure the parser remains reliable across updates and changes.
