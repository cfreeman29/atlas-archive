class ItemParser:
    def parse_items(self, text):
        items = []
        current_item = []
        
        for line in text.split('\n'):
            if line.strip() == '--------':
                if current_item:
                    items.append(self.process_item(current_item))
                    current_item = []
            else:
                current_item.append(line.strip())
                
        if current_item:
            items.append(self.process_item(current_item))
            
        # Combine same items
        combined_items = {}
        for item in items:
            if item:
                name = item['name']
                stack_size = self.parse_stack_size(item['stack_size'])
                
                if name in combined_items:
                    combined_items[name]['stack_size'] += stack_size
                else:
                    combined_items[name] = {
                        'name': name,
                        'stack_size': stack_size,
                        'rarity': item['rarity'],
                        'item_class': item['item_class']
                    }
        
        return list(combined_items.values())
        
    def process_item(self, lines):
        # Basic item processing - can be expanded
        if not lines:
            return None
            
        item_data = {
            'name': 'Unknown Item',
            'rarity': None,
            'item_class': None,
            'stack_size': None
        }
        
        found_rarity = False
        for line in lines:
            if line.startswith('Rarity:'):
                item_data['rarity'] = line.split(': ')[1]
                found_rarity = True
            elif found_rarity and not line.startswith('Item Class:') and not line.startswith('Stack Size:'):
                # The actual item name comes after the Rarity line
                item_data['name'] = line
                found_rarity = False  # Reset so we don't capture description text
            elif line.startswith('Item Class:'):
                item_data['item_class'] = line.split(': ')[1]
            elif line.startswith('Stack Size:'):
                item_data['stack_size'] = line.split(': ')[1]
                
        return item_data
        
    def parse_stack_size(self, stack_size):
        """Convert stack size string to number"""
        if not stack_size:
            return 1
            
        try:
            # Extract current stack size (before the /)
            current = stack_size.split('/')[0]
            return int(current)
        except (ValueError, IndexError):
            return 1
