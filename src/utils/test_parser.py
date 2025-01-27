from item_parser import ItemParser

def print_item(item):
    print(f"Item Class: {item['item_class']}")
    print(f"Rarity: {item['rarity']}")
    print(f"Name: {item['name']}")
    print(f"Stack Size: {item['stack_size']}")
    print("--------")

# Test stackable currency data
currency_data = """Item Class: Stackable Currency
Rarity: Currency
Exalted Orb
--------
Stack Size: 11/20
--------
Augments a Rare item with a new random modifier
--------
Right click this item then left click a rare item to apply it. Rare items can have up to six random modifiers.
Shift click to unstack

Item Class: Stackable Currency
Rarity: Currency
Exalted Orb
--------
Stack Size: 11/20
--------
Augments a Rare item with a new random modifier
--------
Right click this item then left click a rare item to apply it. Rare items can have up to six random modifiers.
Shift click to unstack"""

# Test jewelry data
jewelry_data = """Item Class: Rings
Rarity: Magic
Freezing Amethyst Ring of the Mongoose
--------
Requirements:
Level: 28
--------
Item Level: 80
--------
+11% to Chaos Resistance (implicit)
--------
Adds 9 to 17 Cold damage to Attacks
+8 to Dexterity

Item Class: Amulets
Rarity: Normal
Amber Amulet
--------
Requirements:
Level: 8
--------
Item Level: 79
--------
+13 to Strength (implicit)

Item Class: Rings
Rarity: Rare
Rift Hold
Prismatic Ring
--------
Requirements:
Level: 56
--------
Item Level: 79
--------
+9% to all Elemental Resistances (implicit)
--------
+92 to maximum Life
+110 to maximum Mana
+13 to all Attributes
+39% to Cold Resistance
10.8 Life Regeneration per second"""

# Create parser and test
parser = ItemParser()

print("Testing Stackable Currency:")
items = parser.parse_items(currency_data)
for item in items:
    print_item(item)

print("\nTesting Jewelry:")
items = parser.parse_items(jewelry_data)
for item in items:
    print_item(item)

# Test parsing same data again (should NOT double count since parser state is reset)
print("\nSecond parse of Jewelry (should be same as first):")
items = parser.parse_items(jewelry_data)
for item in items:
    print_item(item)
