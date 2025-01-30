# Item Parser Documentation

The item parser is responsible for parsing item text copied from the game and converting it into structured data that can be displayed in the UI. This document explains how the parser works and how to add support for new item types.

## Overview

The parser works by:
1. Breaking down copied text into blocks separated by "Rarity:" markers
2. Extracting basic item information (class, rarity, name, etc.)
3. Processing each block based on the item class
4. Maintaining counts for each type of item
5. Adding special suffixes for custom UI coloring

## Item Block Structure

A typical item block looks like this:
```
Item Class: Trial Coins
Rarity: Currency
Djinn Barya
--------
Area Level: 80
Number of Trials: 4
--------
Item Level: 81
--------
"Take me to the Trial of the Sekhemas.
I will serve."
--------
Take this item to the Relic Altar at the Trial of the Sekhemas.
```

## Adding a New Item Type

To add support for a new item type, follow these steps:

1. Add a counter in the ItemParser class initialization:
```python
def __init__(self):
    self._items = {}
    self._new_item_counts = {}  # Add counter for new item type
```

2. Add a handler in the parse_items method:
```python
elif current_item['item_class'] == 'Your New Item Class':
    # Handle new item type
    if current_item['name']:
        # Extract any special information from block
        special_info = None
        for line in block:
            if line.startswith('Special Info:'):
                try:
                    special_info = line.split(':', 1)[1].strip()
                    break
                except (ValueError, IndexError):
                    continue
        
        if special_info is not None:
            # Create item name with special info
            name = f"{current_item['name']} ({special_info})"
            # Add suffix for UI coloring if needed
            key = f"{name}_suffix"
            
            # Track counts
            if key not in self._new_item_counts:
                self._new_item_counts[key] = 1
            else:
                self._new_item_counts[key] += 1
```

3. Add items to the final results:
```python
# Add new item counts as separate items
for key, count in self._new_item_counts.items():
    items.append({
        'item_class': 'Your New Item Class',
        'rarity': 'Currency',  # Or appropriate rarity
        'name': key,  # Includes _suffix for UI coloring
        'stack_size': count,
        'display_rarity': 'Normal'  # For UI coloring
    })
```

4. Reset the counter in the state reset section:
```python
# Reset state for next parse
self._items = {}
self._new_item_counts = {}
```

## Examples

### Skill Gems

Skill gems are implemented with:
- Counter: `self._skillgem_counts`
- Suffix: `_skillgem` for silver coloring
- Special info: Level number
- Example output: "Uncut Skill Gem (Level 20)_skillgem"

```python
elif current_item['rarity'] == 'Currency' and any(gem_type in block for gem_type in ['Uncut Skill Gem', 'Uncut Spirit Gem', 'Uncut Support Gem']):
    # Extract level and gem type
    level = None
    gem_type = None
    for line in block:
        if line.startswith('Level:'):
            try:
                level = int(line.split(':', 1)[1].strip())
            except (ValueError, IndexError):
                continue
        elif line in ['Uncut Skill Gem', 'Uncut Spirit Gem', 'Uncut Support Gem']:
            gem_type = line
    
    if level is not None and gem_type is not None:
        name = f"{gem_type} (Level {level})"
        key = f"{name}_skillgem"
        if key not in self._skillgem_counts:
            self._skillgem_counts[key] = 1
        else:
            self._skillgem_counts[key] += 1
```

### Trial Coins

Trial coins are implemented with:
- Counter: `self._trialcoin_counts`
- Suffix: `_trialcoin` for silver coloring
- Special info: Area level
- Example output: "Djinn Barya (Area 80)_trialcoin"

```python
elif current_item['item_class'] == 'Trial Coins':
    # Extract area level
    area_level = None
    for line in block:
        if line.startswith('Area Level:'):
            try:
                area_level = int(line.split(':', 1)[1].strip())
                break
            except (ValueError, IndexError):
                continue
    
    if area_level is not None and current_item['name']:
        name = f"{current_item['name']} (Area {area_level})"
        key = f"{name}_trialcoin"
        if key not in self._trialcoin_counts:
            self._trialcoin_counts[key] = 1
        else:
            self._trialcoin_counts[key] += 1
```

## UI Coloring

To add a new color for your item type:

1. Add the suffix check in item_entry_dialog.py and map_run_details_dialog.py:
```python
# Special color handling
if name.endswith('_pinkey'):
    color = '#ff0000'  # Red for pinnacle keys
elif name.endswith('_skillgem') or name.endswith('_trialcoin') or name.endswith('_your_suffix'):
    color = '#c0c0c0'  # Silver for skill gems and trial coins
else:
    color = rarity_colors.get(rarity, '#cccccc')
```

## Best Practices

1. Always extract special information (level, area, etc.) before creating the item name
2. Use clear and consistent naming for counters and suffixes
3. Handle potential errors in value extraction with try/except blocks
4. Reset all counters in the state reset section
5. Follow existing patterns for similar item types
6. Test with actual game text to ensure correct parsing
