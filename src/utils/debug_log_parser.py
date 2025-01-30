from log_parser import LogParser
from pathlib import Path

# Create empty test log file
test_log = Path("test_client.txt")
test_log.touch()

# Create parser with empty file
parser = LogParser(str(test_log))

# Write test content
with open(test_log, "w", encoding='utf-8') as f:
    f.write('2025/01/30 18:03:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 65 area "MapHiddenGrotto" with seed 1681684543\n')

print("Initial file size:", test_log.stat().st_size)
print("Initial parser position:", parser.last_position)
events = parser.check_updates()
print("First check events:", events)

# Write new content (simulating rotation)
with open(test_log, "w", encoding='utf-8') as f:
    f.write('2025/01/30 18:15:45 3802609 2caa1679 [DEBUG Client 25000] Generating level 75 area "MapCrimsonTemple" with seed 1681684545\n')

# Check again
print("\nNew file size:", test_log.stat().st_size)
print("Parser position before second check:", parser.last_position)
events = parser.check_updates()
print("Second check events:", events)
print("Final parser position:", parser.last_position)

# Print the actual content of the file
print("\nActual file content:")
with open(test_log, 'r', encoding='utf-8') as f:
    print(f.read())

# Clean up
test_log.unlink()
