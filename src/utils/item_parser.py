class ItemParser:
    def __init__(self):
        self._items = {}  # Store items by name
        self._waystone_counts = {}  # Store waystone counts by tier
        self._ring_counts = {}  # Store ring counts by type
        self._amulet_counts = {}  # Store amulet counts by type

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
                    # For rare items, check next line for the actual ring type
                    if current_item['rarity'] == 'Rare':
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
                        name_parts = current_item['name'].split()
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

            elif current_item['item_class'] == 'Amulets':
                # Handle amulets - extract type and count occurrences
                if current_item['name']:
                    # Find the word before "Amulet" in the name
                    name_parts = current_item['name'].split()
                    for i, part in enumerate(name_parts):
                        if part == 'Amulet' and i > 0:
                            amulet_type = name_parts[i-1]
                            # Strip any existing 'xN' from the name
                            amulet_type = amulet_type.split(' x')[0]
                            key = f"{amulet_type} Amulet"
                            if key not in self._amulet_counts:
                                self._amulet_counts[key] = 1
                            else:
                                self._amulet_counts[key] += 1
                            break
        
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

        # Reset state for next parse
        self._items = {}
        self._waystone_counts = {}
        self._ring_counts = {}
        self._amulet_counts = {}
        return items
