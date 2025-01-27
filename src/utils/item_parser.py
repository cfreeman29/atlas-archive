class ItemParser:
    def __init__(self):
        self._items = {}  # Store items by name

    def parse_items(self, text):
        """Parse item text and return list of item dictionaries."""
        # Split text into blocks using the separator
        blocks = []
        current_block = []
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            if line == '--------':
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                current_block.append(line)
        
        if current_block:
            blocks.append(current_block)
        
        # Process all blocks
        current_item = {
            'item_class': None,
            'rarity': None,
            'name': None,
            'stack_size': None
        }
        
        for block in blocks:
            if not block:  # Skip empty blocks
                continue
            
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
            
            # If we have both name and amount, update the totals
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
        
        # Get items and clear state
        items = list(self._items.values())
        self._items = {}  # Reset state for next parse
        return items
