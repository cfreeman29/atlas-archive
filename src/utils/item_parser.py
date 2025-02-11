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
        self._relic_counts = {}  # Store relic counts by type
        self._tablet_counts = {}  # Store tablet counts by type
        
        # Store rarity information for each item type
        self._ring_rarities = {}
        self._amulet_rarities = {}
        self._armor_rarities = {}
        self._weapon_rarities = {}
        self._jewel_rarities = {}
        self._relic_rarities = {}
        self._tablet_rarities = {}
        self._pinnacle_key_counts = {}  # Store pinnacle key counts by type
        self._trials_counts = {}  # Store trials item counts by type
        self._gem_counts = {}  # Store gem counts by type
        self._socketable_counts = {}  # Store socketable counts by type
        self._flask_counts = {}  # Store flask counts by type
        self._flask_rarities = {}  # Store flask rarity information
        self._charm_counts = {}  # Store charm counts by type
        self._charm_rarities = {}  # Store charm rarity information

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
        
        # Find blocks by looking for Item Class or Rarity markers
        for line in lines:
            if line.startswith('Item Class:') or (line.startswith('Rarity:') and not current_block):
                if current_block:  # Save previous block if exists
                    blocks.append(current_block)
                current_block = [line]  # Start new block
                # If it's a Rarity line without Item Class, add a default Item Class for gems
                if line.startswith('Rarity:'):
                    # Check if this is a gem item
                    is_gem = False
                    for i, next_line in enumerate(lines[lines.index(line):]):
                        if 'Uncut' in next_line and 'Gem' in next_line:
                            is_gem = True
                            break
                    current_block.insert(0, 'Item Class: Gems' if is_gem else 'Item Class: Stackable Currency')
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
                'stack_size': 1,  # Default to 1
                'waystone_tier': None,
                'display_rarity': None  # For UI coloring
            }
            
            # Extract item details from block
            for i, line in enumerate(block):
                if line.startswith('Item Class:'):
                    current_item['item_class'] = line.split(':', 1)[1].strip()
                    # Item name is two lines after Item Class (after Rarity line)
                    if i + 2 < len(block):
                        current_item['name'] = block[i + 2]
                elif line.startswith('Rarity:'):
                    rarity = line.split(':', 1)[1].strip()
                    current_item['rarity'] = rarity
                    current_item['display_rarity'] = rarity  # Set display rarity when parsing
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
            if current_item['item_class'] == 'Gems':
                # Handle gems - extract level and count occurrences
                if current_item['name']:
                    # Extract gem level
                    gem_level = None
                    for line in block:
                        if line.startswith('Level:'):
                            try:
                                gem_level = int(line.split(':', 1)[1].strip())
                                break
                            except (ValueError, IndexError):
                                continue
                    
                    if gem_level is not None:
                        # Strip any existing 'xN' from the name
                        name = current_item['name'].split(' x')[0]
                        # Add level to name
                        key = f"{name} {gem_level}_gem"  # Add _gem suffix for silver display
                        if key not in self._gem_counts:
                            self._gem_counts[key] = 1
                        else:
                            self._gem_counts[key] += 1
                        # Skip the default currency handling
                        current_item['stack_size'] = None

            elif current_item['item_class'] == 'Stackable Currency':
                # Handle stackable currency - combine stack sizes
                if current_item['name'] and current_item['stack_size']:
                    name = f"{current_item['name']}_{current_item['rarity']}"  # Append rarity to name
                    if name in self._items:
                        # Update existing item's stack size
                        self._items[name]['stack_size'] += current_item['stack_size']
                    else:
                        # Add new item with Currency display rarity
                        item_copy = current_item.copy()
                        item_copy['name'] = name  # Store name with rarity
                        item_copy['display_rarity'] = 'Currency'
                        self._items[name] = item_copy
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
                            self._ring_rarities[name] = 'Unique'
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
                                            self._ring_rarities[key] = 'Rare'
                                        else:
                                            self._ring_counts[key] += 1
                                        break
                    else:
                        # For non-rare items, process normally
                        base_type = self._extract_base_type(current_item['name'], ['Ring'])
                        if base_type:
                            key = f"{base_type}_{current_item['rarity']}"
                            if key not in self._ring_counts:
                                self._ring_counts[key] = 1
                                self._ring_rarities[key] = current_item['rarity']
                            else:
                                self._ring_counts[key] += 1

            elif current_item['item_class'] == 'Charms':
                # Handle charms - extract type and count occurrences
                if current_item['name']:
                    # Get the base name by splitting on 'of' and taking first part
                    name = current_item['name'].split(' of ')[0]
                    # Split into words and look for Charm
                    words = name.split()
                    charm_type = None
                    for i, word in enumerate(words):
                        if word == 'Charm' and i > 0:
                            # Take the word before Charm
                            charm_type = f"{words[i-1]} {word}"
                            break
                    
                    if charm_type:
                        # Add _charm suffix and store rarity
                        key = f"{charm_type}_charm"
                        if key not in self._charm_counts:
                            self._charm_counts[key] = 1
                            self._charm_rarities[key] = current_item['rarity']
                        else:
                            self._charm_counts[key] += 1
                        # Skip the default currency handling
                        current_item['stack_size'] = None

            elif current_item['item_class'] in ['Life Flasks', 'Mana Flasks']:
                # Handle flasks - extract type and count occurrences
                if current_item['name']:
                    # Get the base name by splitting on 'of' and taking first part
                    name = current_item['name'].split(' of ')[0]
                    # Split into words and look for Life/Mana Flask
                    words = name.split()
                    flask_type = None
                    for i, word in enumerate(words):
                        if word in ['Flask'] and i > 0:
                            if words[i-1] in ['Life', 'Mana']:
                                # Take the word before Life/Mana Flask if it exists
                                if i > 1:
                                    flask_type = f"{words[i-2]} {words[i-1]} {word}"
                                else:
                                    flask_type = f"{words[i-1]} {word}"
                                break
                    
                    if flask_type:
                        # Add _flask suffix and store rarity
                        key = f"{flask_type}_flask"
                    if key not in self._flask_counts:
                        self._flask_counts[key] = 1
                        self._flask_rarities[key] = current_item['rarity']
                    else:
                        self._flask_counts[key] += 1
                    # Skip the default currency handling
                    current_item['stack_size'] = None

            elif current_item['item_class'] == 'Socketable':
                # Handle socketables - count occurrences and mark for light blue display
                if current_item['name']:
                    # Strip any existing 'xN' from the name
                    name = current_item['name'].split(' x')[0]
                    key = f"{name}_socket"  # Add _socket suffix for light blue display
                    if key not in self._socketable_counts:
                        self._socketable_counts[key] = 1
                    else:
                        self._socketable_counts[key] += 1
                    # Skip the default currency handling
                    current_item['stack_size'] = None

            elif current_item['item_class'] == 'Amulets':
                # Handle amulets - extract type and count occurrences
                if current_item['name']:
                    # For unique items, use the unique name
                    if current_item['rarity'] == 'Unique':
                        # Strip any existing 'xN' from the name
                        name = current_item['name'].split(' x')[0]
                        if name not in self._amulet_counts:
                            self._amulet_counts[name] = 1
                            self._amulet_rarities[name] = 'Unique'
                        else:
                            self._amulet_counts[name] += 1
                    # For rare items, check next line for the actual amulet type
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
                            amulet_line = blocks[block_index][blocks[block_index].index(current_item['name']) + 1]
                            if 'Amulet' in amulet_line:
                                name_parts = amulet_line.split()
                                for i, part in enumerate(name_parts):
                                    if part == 'Amulet' and i > 0:
                                        amulet_type = name_parts[i-1]
                                        # Strip any existing 'xN' from the name
                                        amulet_type = amulet_type.split(' x')[0]
                                        key = f"{amulet_type} Amulet"
                                        if key not in self._amulet_counts:
                                            self._amulet_counts[key] = 1
                                            self._amulet_rarities[key] = 'Rare'
                                        else:
                                            self._amulet_counts[key] += 1
                                        break
                    else:
                        # For non-rare items, process normally
                        base_type = self._extract_base_type(current_item['name'], ['Amulet'])
                        if base_type:
                            key = f"{base_type}_{current_item['rarity']}"
                            if key not in self._amulet_counts:
                                self._amulet_counts[key] = 1
                                self._amulet_rarities[key] = current_item['rarity']
                            else:
                                self._amulet_counts[key] += 1

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
                        key = f"{base_type}_{current_item['rarity']}"
                        if key not in self._weapon_counts:
                            self._weapon_counts[key] = 1
                            self._weapon_rarities[key] = current_item['rarity']
                        else:
                            self._weapon_counts[key] += 1

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
                        key = f"{base_type}_{current_item['rarity']}"
                        if key not in self._jewel_counts:
                            self._jewel_counts[key] = 1
                            self._jewel_rarities[key] = current_item['rarity']
                        else:
                            self._jewel_counts[key] += 1

            elif current_item['item_class'] == 'Relics':
                # Handle relics - extract type and count occurrences
                if current_item['name']:
                    base_type = None
                    if current_item['rarity'] == 'Magic':
                        # For magic items, extract base type from the name
                        base_type = self._extract_base_type(current_item['name'], ['Relic'])
                    else:
                        # For other rarities, use full name
                        base_type = current_item['name']
                    
                    if base_type:
                        # Strip any existing 'xN' from the name
                        base_type = base_type.split(' x')[0]
                        key = f"{base_type}_{current_item['rarity']}"
                        if key not in self._relic_counts:
                            self._relic_counts[key] = 1
                            self._relic_rarities[key] = current_item['rarity']
                        else:
                            self._relic_counts[key] += 1

            elif current_item['item_class'] == 'Pinnacle Keys':
                # Handle pinnacle keys - count occurrences and mark for red display
                if current_item['name']:
                    # Strip any existing 'xN' from the name
                    name = current_item['name'].split(' x')[0]
                    key = f"{name}_pinkey"  # Add _pinkey suffix for red display
                    if key not in self._pinnacle_key_counts:
                        self._pinnacle_key_counts[key] = 1
                    else:
                        self._pinnacle_key_counts[key] += 1

            elif current_item['item_class'] == 'Tablet':
                # Handle tablets - extract type and count occurrences
                if current_item['name']:
                    base_type = None
                    tablet_types = [
                        'Breach Precursor Tablet',
                        'Expedition Precursor Tablet',
                        'Delirium Precursor Tablet',
                        'Ritual Precursor Tablet',
                        'Precursor Tablet',
                        'Overseer Precursor Tablet'
                    ]
                    
                    if current_item['rarity'] == 'Magic':
                        # For magic items, extract the base tablet type
                        name = current_item['name'].split(' of ')[0]  # Remove 'of X' suffix
                        # Find which tablet type this is by looking for "Precursor Tablet"
                        if 'Precursor Tablet' in name:
                            # Check if it's a special type
                            for tablet_type in tablet_types:
                                if tablet_type != 'Precursor Tablet' and all(word in name for word in tablet_type.split()):
                                    base_type = tablet_type
                                    break
                            # If no special type found, use base Precursor Tablet
                            if not base_type:
                                base_type = 'Precursor Tablet'
                    else:
                        # For normal items, use the exact name if it matches a known type
                        if current_item['name'] in tablet_types:
                            base_type = current_item['name']
                    
                    if base_type:
                        # Strip any existing 'xN' from the name
                        base_type = base_type.split(' x')[0]
                        key = f"{base_type}_{current_item['rarity']}"
                        if key not in self._tablet_counts:
                            self._tablet_counts[key] = 1
                            self._tablet_rarities[key] = current_item['rarity']
                        else:
                            self._tablet_counts[key] += 1

            elif current_item['item_class'] in ['Inscribed Ultimatum', 'Trial Coins']:
                # Handle trials items - count occurrences and mark for rust display
                if current_item['name']:
                    # Check for trials-related fields
                    has_trials = False
                    for line in block:
                        if 'Number of Trials:' in line or 'Trial' in current_item['name'] or 'Ultimatum' in current_item['name']:
                            has_trials = True
                            break
                    
                    if has_trials:
                        # Strip any existing 'xN' from the name
                        name = current_item['name'].split(' x')[0]
                        key = f"{name}_trials"  # Add _trials suffix for rust display
                        if key not in self._trials_counts:
                            self._trials_counts[key] = 1
                        else:
                            self._trials_counts[key] += 1

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
                        key = f"{base_type}_{current_item['rarity']}"
                        if key not in self._armor_counts:
                            self._armor_counts[key] = 1
                            self._armor_rarities[key] = current_item['rarity']
                        else:
                            self._armor_counts[key] += 1
        
        # Combine results from both parsing methods
        items = list(self._items.values())
        
        # Add waystone counts as separate items
        for key, count in self._waystone_counts.items():
            items.append({
                'item_class': 'Waystones',
                'rarity': 'Normal',
                'name': key,
                'stack_size': count,
                'display_rarity': 'Normal'  # For UI coloring
            })
        
        # Add ring counts as separate items
        for key, count in self._ring_counts.items():
            rarity = self._ring_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Rings',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add amulet counts as separate items
        for key, count in self._amulet_counts.items():
            rarity = self._amulet_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Amulets',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add armor counts as separate items
        for key, count in self._armor_counts.items():
            rarity = self._armor_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Armor',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add weapon counts as separate items
        for key, count in self._weapon_counts.items():
            rarity = self._weapon_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Weapons',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add omen counts as separate items
        for key, count in self._omen_counts.items():
            items.append({
                'item_class': 'Omen',
                'rarity': 'Currency',
                'name': key,
                'stack_size': count,
                'display_rarity': 'Currency'  # For UI coloring
            })

        # Add jewel counts as separate items
        for key, count in self._jewel_counts.items():
            rarity = self._jewel_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Jewels',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add relic counts as separate items
        for key, count in self._relic_counts.items():
            rarity = self._relic_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Relics',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add tablet counts as separate items
        for key, count in self._tablet_counts.items():
            rarity = self._tablet_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Tablet',
                'rarity': rarity,
                'name': key,
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring
            })

        # Add pinnacle key counts as separate items
        for key, count in self._pinnacle_key_counts.items():
            items.append({
                'item_class': 'Pinnacle Keys',
                'rarity': 'Currency',
                'name': key,  # Includes _pinkey suffix for red display
                'stack_size': count,
                'display_rarity': 'Currency'  # For UI coloring
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
        self._ring_rarities = {}
        self._amulet_rarities = {}
        self._armor_rarities = {}
        self._weapon_rarities = {}
        self._jewel_rarities = {}
        self._relic_counts = {}
        self._relic_rarities = {}
        self._tablet_counts = {}
        self._tablet_rarities = {}
        self._pinnacle_key_counts = {}

        # Add trials item counts as separate items
        for key, count in self._trials_counts.items():
            items.append({
                'item_class': 'Trials',
                'rarity': 'Currency',
                'name': key,  # Includes _trials suffix for rust display
                'stack_size': count,
                'display_rarity': 'Currency'  # For UI coloring
            })

        # Reset trials counts
        self._trials_counts = {}

        # Add gem counts as separate items
        for key, count in self._gem_counts.items():
            items.append({
                'item_class': 'Gems',
                'rarity': 'Currency',
                'name': key,  # Includes _gem suffix for silver display
                'stack_size': count,
                'display_rarity': 'Currency'  # For UI coloring
            })

        # Reset gem counts
        self._gem_counts = {}

        # Add socketable counts as separate items
        for key, count in self._socketable_counts.items():
            items.append({
                'item_class': 'Socketable',
                'rarity': 'Currency',
                'name': key,  # Includes _socket suffix for light blue display
                'stack_size': count,
                'display_rarity': 'Currency'  # For UI coloring
            })

        # Add flask counts as separate items
        for key, count in self._flask_counts.items():
            rarity = self._flask_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Flasks',
                'rarity': rarity,
                'name': key,  # Includes _flask suffix
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring based on rarity
            })

        # Reset flask counts
        self._flask_counts = {}
        self._flask_rarities = {}

        # Add charm counts as separate items
        for key, count in self._charm_counts.items():
            rarity = self._charm_rarities.get(key, 'Normal')
            items.append({
                'item_class': 'Charms',
                'rarity': rarity,
                'name': key,  # Includes _charm suffix
                'stack_size': count,
                'display_rarity': rarity  # For UI coloring based on rarity
            })

        # Reset charm counts
        self._charm_counts = {}
        self._charm_rarities = {}

        # Reset socketable counts
        self._socketable_counts = {}
        return items
