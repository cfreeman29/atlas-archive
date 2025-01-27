from item_parser import ItemParser

def print_item(item):
    print(f"Item Class: {item['item_class']}")
    print(f"Rarity: {item['rarity']}")
    print(f"Name: {item['name']}")
    print(f"Stack Size: {item['stack_size']}")
    print("--------")

# Test data
test_data = """Item Class: Stackable Currency
Rarity: Currency
Exalted Orb
--------
Stack Size: 11/20
--------
Augments a Rare item with a new random modifier
--------
Right click this item then left click a rare item to apply it. Rare items can have up to six random modifiers.
Shift click to unstack."""

# Create parser and test
parser = ItemParser()
print("First parse:")
items = parser.parse_items(test_data)
for item in items:
    print_item(item)

# Test parsing same data again (should NOT double stack size since parser state is reset)
print("\nSecond parse (should be same as first):")
items = parser.parse_items(test_data)
for item in items:
    print_item(item)
