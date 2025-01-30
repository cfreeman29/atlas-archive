# Item Parser Documentation

## Overview

The item parser system in Atlas Archive is designed to handle various types of Path of Exile 2 items. It processes clipboard text from the game and categorizes items based on their class, rarity, and special attributes. This document explains how the system works and how to extend it.

## Item Structure

Each item in PoE2 follows this general structure in clipboard text:

```
Item Class: [Class Name]
Rarity: [Rarity Type]
[Item Name]
--------
[Additional Fields...]
--------
```

## How Item Parsing Works

1. The parser splits the clipboard text into blocks separated by `Item Class:` markers
2. For each block:
   - Extracts basic item information (class, rarity, name)
   - Processes special fields (e.g., stack size, waystone tier)
   - Routes the item to the appropriate handler based on its class
3. Items are stored with standardized properties:
   ```python
   {
       'item_class': str,      # The item's class
       'rarity': str,         # Original rarity
       'name': str,          # Item name (may include suffix for special items)
       'stack_size': int,    # Quantity of the item
       'display_rarity': str # Used for UI coloring
   }
   ```

## Item Types and Their Handlers

### 1. Stackable Currency
- Combines identical items by adding their stack sizes
- Appends rarity to name: `{name}_{rarity}`
- Sets display_rarity to 'Currency'

### 2. Waystones
- Identifies by 'Waystone Tier:' field
- Groups by tier: `Waystone T{tier}`
- Uses Normal rarity coloring

### 3. Rings & Amulets
- Handles unique items by name
- For rare items: extracts base type from line after name
- For magic/normal: uses word before "Ring"/"Amulet"
- Key format: `{base_type}_{rarity}`

### 4. Weapons
- Supports multiple weapon classes (Wands, Bows, etc.)
- Unique items: uses full name
- Rare items: gets base type from next line
- Magic/normal: extracts type using keywords
- Key format: `{base_type}_{rarity}`

### 5. Jewels
- Uses jewel keywords (Sapphire, Emerald, etc.)
- Unique items: uses full name
- Rare/magic: extracts base type
- Key format: `{base_type}_{rarity}`

### 6. Relics
- Magic items: extracts base type using 'Relic' keyword
- Other rarities: uses full name
- Key format: `{base_type}_{rarity}`

### 7. Pinnacle Keys
- Adds '_pinkey' suffix for red coloring
- Uses Currency rarity
- Key format: `{name}_pinkey`

### 8. Tablets
- Supports various tablet types (Breach, Expedition, etc.)
- Magic items: extracts tablet type
- Normal items: matches against known types
- Key format: `{base_type}_{rarity}`

### 9. Trials Items
- Identifies by:
  - "Number of Trials:" field
  - "Trial" or "Ultimatum" in name
- Adds '_trials' suffix for rust coloring
- Uses Currency rarity
- Key format: `{name}_trials`

### 10. Omens
- Simple counting by name
- Uses Currency rarity

### 11. Armor
- Supports multiple armor types (Helmets, Boots, etc.)
- Similar handling to weapons
- Key format: `{base_type}_{rarity}`

## Adding New Item Types

1. Add storage in ItemParser class:
   ```python
   def __init__(self):
       self._new_type_counts = {}
       self._new_type_rarities = {}
   ```

2. Add handler in parse_items method:
   ```python
   elif current_item['item_class'] == 'New Type':
       if current_item['name']:
           # Process item
           # Add to appropriate counts/rarities
   ```

3. Add to results compilation:
   ```python
   # Add new type counts as separate items
   for key, count in self._new_type_counts.items():
       rarity = self._new_type_rarities.get(key, 'Normal')
       items.append({
           'item_class': 'New Type',
           'rarity': rarity,
           'name': key,
           'stack_size': count,
           'display_rarity': rarity
       })
   ```

4. Add to reset state section:
   ```python
   self._new_type_counts = {}
   self._new_type_rarities = {}
   ```

## Special Display Handling

To add custom coloring for items:

1. In item_entry_dialog.py and map_run_details_dialog.py:
   ```python
   # Color mapping based on rarity and special suffixes
   rarity_colors = {
       'Normal': '#ffffff',   # White
       'Magic': '#8888ff',    # Blue
       'Rare': '#ffff77',     # Yellow
       'Unique': '#af6025',   # Orange/Brown
       'Currency': '#aa9e82'  # Currency color
   }
   ```

2. For special items, add suffix check:
   ```python
   if name.endswith('_suffix'):
       color = '#color_code'  # Your color
   ```

Current special suffixes:
- `_pinkey`: Red color (#ff0000)
- `_trials`: Rust color (#b7410e)

## Testing New Items

1. Add test data to test_parser.py:
   ```python
   # Test new type data
   new_type_data = """Item Class: New Type
   Rarity: Normal
   Test Item Name
   --------
   [Additional Fields]
   """
   ```

2. Add test case:
   ```python
   print("\nTesting New Type Items:")
   items = parser.parse_items(new_type_data)
   for item in items:
       print_item(item)
   ```

3. Run test:
   ```bash
   python src/utils/test_parser.py
   ```

4. Verify output shows:
   - Correct item class
   - Correct rarity
   - Correct name (with any suffixes)
   - Correct stack size

## Common Issues to Watch For

1. **Item Block Detection**
   - Always starts with "Item Class:"
   - Ensure proper block separation

2. **Name Processing**
   - Handle 'x[N]' stack indicators
   - Consider 'of' suffixes in magic items

3. **Rarity Handling**
   - Set both 'rarity' and 'display_rarity'
   - Consider special cases (Currency items)

4. **Special Fields**
   - Check field format consistency
   - Handle missing or malformed fields

5. **Color Display**
   - Update both dialog files for new colors
   - Test with different color themes

## Best Practices

1. Always add test cases for new item types
2. Document special handling requirements
3. Update both dialog files for UI changes
4. Test with various item variations
5. Consider edge cases (missing fields, malformed data)
6. Keep naming conventions consistent
7. Reset all state variables after parsing
