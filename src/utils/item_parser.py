class ItemParser:
    def __init__(self):
        self._items = {}  # Store items by name
        self._waystone_counts = {}  # Store waystone counts by tier
        self._ring_counts = {}  # Store ring counts by type
        self._amulet_counts = {}  # Store amulet counts by type
        self._armor_counts = {}  # Store armor counts by type
        self._weapon_counts = {}  # Store weapon counts by type
        self._omen_counts = {}  # Store omen counts by type
        self._jewel_counts = {}  # Store jewel counts by type

    def _extract_base_type(self, name, keywords):
        """Helper to extract base type from a magic/normal item name."""
        # First split on 'of' to remove any suffixes
        name = name.split(' of ')[0]
        name_parts = name.split()
        
        for i, part in enumerate(name_parts):
            if part in keywords and i > 0:
                # For rings and amulets, take just the word before
                if part in ['Ring', 'Amulet']:
                    return f"{name_parts[i-1]} {part}"
                
                # For armor pieces, take the last two words (including the keyword)
                # This handles cases like "Innovative Plate Belt" -> "Plate Belt"
                if i > 1:
                    return f"{name_parts[i-1]} {part}"
                else:
                    return f"{name_parts[i]}"
        return None

    def parse_items(self, text):
        """Parse item text and return list of item dictionaries."""
        # Split into lines and clean up
        lines = [line.strip() for line in text.split('\n') if line.strip() and line.strip() != '--------']
        blocks = []
        current_block = []
        
        # Find blocks by looking for Item Class markers
        for line in lines:
            if line.startswith('Item Class:'):
                if current_block:  # Save previous block if exists
                    blocks.append(current_block)
                current_block = [line]  # Start new block
            elif current_block is not None:  # Add to current block if one exists
                current_block.append(line)
                
        # Add final block if exists
        if current_block:
            blocks.append(current_block)
        
        # Process all blocks
        for block in blocks:
            if not block:  # Skip empty blocks
                continue
                
            # Reset current_item for each new block
            current_item = {
                'item_class': None,
                'rarity': None,
                'name': None,
                'stack_size': None,
                'waystone_tier': None
            }
            
            # Extract item details from block
            for i, line in enumerate(block):
                if line.startswith('Item Class:'):
                    current_item['item_class'] = line.split(':', 1)[1].strip()
                    # Item name is two lines after Item Class (after Rarity line)
                    if i + 2 < len(block):
                        current_item['name'] = block[i + 2]
                elif line.startswith('Rarity:'):
                    current_item['rarity'] = line.split(':', 1)[1].strip()
                elif line.startswith('Stack Size:'):
                    try:
                        amount = int(line.split(':', 1)[1].strip().split('/')[0])
                        current_item['stack_size'] = amount
                    except (ValueError, IndexError):
                        continue
                elif line.startswith('Waystone Tier:'):
                    try:
                        tier = int(line.split(':', 1)[1].strip())
                        current_item['waystone_tier'] = tier
                    except (ValueError, IndexError):
                        continue

            # Handle different item classes
            if current_item['item_class'] == 'Stackable Currency':
                # Handle stackable currency - combine stack sizes
                if current_item['name'] and current_item['stack_size']:
                    name = current_item['name']
                    if name in self._items:
                        # Update existing item's stack size
                        self._items[name]['stack_size'] += current_item['stack_size']
                    else:
                        # Add new item
                        self._items[name] = current_item.copy()
                    # Reset stack size but keep other item details
                    current_item['stack_size'] = None

            elif current_item['item_class'] == 'Waystones':
                # Handle waystones - count occurrences
                if current_item.get('waystone_tier'):
                    tier = current_item['waystone_tier']
                    # Strip any existing 'xN' from the name
                    name = current_item['name'].split(' x')[0]
                    key = f"Waystone T{tier}"
                    if key not in self._waystone_counts:
                        self._waystone_counts[key] = 1
                    else:
                        self._waystone_counts[key] += 1

            elif current_item['item_class'] == 'Rings':
                # Handle rings - extract type and count occurrences
                if current_item['name']:
                    # For unique items, use the unique name
                    if current_item['rarity'] == 'Unique':
                        # Strip any existing 'xN' from the name
                        name = current_item['name'].split(' x')[0]
                        if name not in self._ring_counts:
                            self._ring_counts[name] = 1
                        else:
                            self._ring_counts[name] += 1
                    # For rare items, check next line for the actual ring type
                    elif current_item['rarity'] == 'Rare':
                        # Get the next line after the rare name
                        block_index = None
                        for i, block in enumerate(blocks):
                            for line in block:
                                if line == current_item['name']:
                                    block_index = i
                                    break
                            if block_index is not None:
                                break
                        
                        if block_index is not None and len(blocks[block_index]) > blocks[block_index].index(current_item['name']) + 1:
                            ring_line = blocks[block_index][blocks[block_index].index(current_item['name']) + 1]
                            if 'Ring' in ring_line:
                                name_parts = ring_line.split()
                                for i, part in enumerate(name_parts):
                                    if part == 'Ring' and i > 0:
                                        ring_type = name_parts[i-1]
                                        # Strip any existing 'xN' from the name
                                        ring_type = ring_type.split(' x')[0]
                                        key = f"{ring_type} Ring"
                                        if key not in self._ring_counts:
                                            self._ring_counts[key] = 1
                                        else:
                                            self._ring_counts[key] += 1
                                        break
                    else:
                        # For non-rare items, process normally
                        base_type = self._extract_base_type(current_item['name'], ['Ring'])
                        if base_type:
                            if base_type not in self._ring_counts:
                                self._ring_counts[base_type] = 1
                            else:
                                self._ring_counts[base_type] += 1

            elif current_item['item_class'] == 'Amulets':
                # Handle amulets - extract type and count occurrences
                if current_item['name']:
                    if current_item['rarity'] == 'Unique':
                        # For unique items, use the unique name
                        name = current_item['name'].split(' x')[0]
                        if name not in self._amulet_counts:
                            self._amulet_counts[name] = 1
                        else:
                            self._amulet_counts[name] += 1
                    else:
                        # For non-unique items, find the word before "Amulet" in the name
                        base_type = self._extract_base_type(current_item['name'], ['Amulet'])
                        if base_type:
                            if base_type not in self._amulet_counts:
                                self._amulet_counts[base_type] = 1
                            else:
                                self._amulet_counts[base_type] += 1

            elif current_item['item_class'] in ['Wands', 'Two Hand Maces', 'Bows', 'Staves', 'Quivers', 'Shields', 'Crossbows', 'Foci', 'Sceptres', 'Quarterstaves']:
                # Handle weapons - extract base type and count occurrences
                if current_item['name']:
                    base_type = None
                    weapon_keywords = {
                        'Wands': ['Wand'],
                        'Two Hand Maces': ['Greathammer', 'Mace'],
                        'Bows': ['Bow'],
                        'Staves': ['Staff'],
                        'Quivers': ['Quiver'],
                        'Shields': ['Shield', 'Buckler'],
                        'Crossbows': ['Crossbow'],
                        'Foci': ['Focus'],
                        'Sceptres': ['Sceptre'],
                        'Quarterstaves': ['Quarterstaff']
                    }
                    
                    keywords = weapon_keywords[current_item['item_class']]
                    
                    if current_item['rarity'] == 'Unique':
                        # For unique items, use the unique name instead of base type
                        base_type = current_item['name']
                    elif current_item['rarity'] == 'Rare':
                        # Get the base type from the line after the name
                        block_index = None
                        for i, block in enumerate(blocks):
                            for line in block:
                                if line == current_item['name']:
                                    block_index = i
                                    break
                            if block_index is not None:
                                break
                        
                        if block_index is not None and len(blocks[block_index]) > blocks[block_index].index(current_item['name']) + 1:
                            base_type = blocks[block_index][blocks[block_index].index(current_item['name']) + 1]
                    else:
                        # For magic/normal items, extract base type from the single line name
                        base_type = self._extract_base_type(current_item['name'], keywords)
                    
                    if base_type:
                        # Strip any existing 'xN' from the name
                        base_type = base_type.split(' x')[0]
                        if base_type not in self._weapon_counts:
                            self._weapon_counts[base_type] = 1
                        else:
                            self._weapon_counts[base_type] += 1

            elif current_item['item_class'] == 'Jewels':
                # Handle jewels - extract type and count occurrences
                if current_item['name']:
                    base_type = None
                    jewel_keywords = ['Sapphire', 'Emerald', 'Ruby', 'Topaz', 'Amethyst', 'Diamond']
                    
                    if current_item['rarity'] == 'Unique':
                        # For unique items, use the unique name
                        base_type = current_item['name']
                    elif current_item['rarity'] == 'Rare':
                        # Get the base type from the line after the name
                        block_index = None
                        for i, block in enumerate(blocks):
                            for line in block:
                                if line == current_item['name']:
                                    block_index = i
                                    break
                            if block_index is not None:
                                break
                        
                        if block_index is not None and len(blocks[block_index]) > blocks[block_index].index(current_item['name']) + 1:
                            base_type = blocks[block_index][blocks[block_index].index(current_item['name']) + 1]
                    else:
                        # For magic/normal items, extract base type from the name
                        name = current_item['name'].split(' of ')[0]  # Remove 'of X' suffix
                        for keyword in jewel_keywords:
                            if keyword in name:
                                base_type = keyword
                                break
                    
                    if base_type:
                        # Strip any existing 'xN' from the name
                        base_type = base_type.split(' x')[0]
                        if base_type not in self._jewel_counts:
                            self._jewel_counts[base_type] = 1
                        else:
                            self._jewel_counts[base_type] += 1

            elif current_item['item_class'] == 'Omen':
                # Handle omens - count occurrences
                if current_item['name']:
                    # Strip any existing 'xN' from the name
                    name = current_item['name'].split(' x')[0]
                    if name not in self._omen_counts:
                        self._omen_counts[name] = 1
                    else:
                        self._omen_counts[name] += 1

            elif current_item['item_class'] in ['Helmets', 'Body Armours', 'Gloves', 'Boots', 'Belts']:
                # Handle armor pieces - extract base type and count occurrences
                if current_item['name']:
                    base_type = None
                    armor_keywords = {
                        'Helmets': ['Hood', 'Helm', 'Helmet', 'Crown', 'Mask'],
                        'Body Armours': ['Vest', 'Armour', 'Plate', 'Garb', 'Robe'],
                        'Gloves': ['Gloves', 'Gauntlets', 'Mitts', 'Wraps'],
                        'Boots': ['Boots', 'Greaves', 'Slippers'],
                        'Belts': ['Belt', 'Sash', 'Stash']
                    }
                    
                    keywords = armor_keywords[current_item['item_class']]
                    
                    if current_item['rarity'] == 'Unique':
                        # For unique items, use the unique name
                        base_type = current_item['name']
                    elif current_item['rarity'] == 'Rare':
                        # Get the base type from the line after the name
                        block_index = None
                        for i, block in enumerate(blocks):
                            for line in block:
                                if line == current_item['name']:
                                    block_index = i
                                    break
                            if block_index is not None:
                                break
                        
                        if block_index is not None and len(blocks[block_index]) > blocks[block_index].index(current_item['name']) + 1:
                            base_type = blocks[block_index][blocks[block_index].index(current_item['name']) + 1]
                    else:
                        # For magic/normal items, extract base type from the name
                        name = current_item['name'].split(' of ')[0]  # Remove 'of X' suffix
                        # Try to find any of the keywords in the name
                        for keyword in keywords:
                            if keyword in name:
                                # Get the word before the keyword if it exists
                                name_parts = name.split()
                                keyword_index = name_parts.index(keyword)
                                if keyword_index > 0:
                                    base_type = f"{name_parts[keyword_index-1]} {keyword}"
                                else:
                                    base_type = keyword
                                break
                    
                    if base_type:
                        # Strip any existing 'xN' from the name
                        base_type = base_type.split(' x')[0]
                        if base_type not in self._armor_counts:
                            self._armor_counts[base_type] = 1
                        else:
                            self._armor_counts[base_type] += 1
        
        # Combine results from both parsing methods
        items = list(self._items.values())
        
        # Add waystone counts as separate items
        for key, count in self._waystone_counts.items():
            items.append({
                'item_class': 'Waystones',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count
            })
        
        # Add ring counts as separate items
        for key, count in self._ring_counts.items():
            items.append({
                'item_class': 'Rings',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count
            })

        # Add amulet counts as separate items
        for key, count in self._amulet_counts.items():
            items.append({
                'item_class': 'Amulets',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count
            })

        # Add armor counts as separate items
        for key, count in self._armor_counts.items():
            items.append({
                'item_class': 'Armor',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count
            })

        # Add weapon counts as separate items
        for key, count in self._weapon_counts.items():
            items.append({
                'item_class': 'Weapons',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count
            })

        # Add omen counts as separate items
        for key, count in self._omen_counts.items():
            items.append({
                'item_class': 'Omen',
                'rarity': 'Currency',
                'name': key,
                'stack_size': count
            })

        # Add jewel counts as separate items
        for key, count in self._jewel_counts.items():
            items.append({
                'item_class': 'Jewels',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count
            })

        # Reset state for next parse
        self._items = {}
        self._waystone_counts = {}
        self._ring_counts = {}
        self._amulet_counts = {}
        self._armor_counts = {}
        self._weapon_counts = {}
        self._omen_counts = {}
        self._jewel_counts = {}
        return items
