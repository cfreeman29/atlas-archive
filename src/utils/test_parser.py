from item_parser import ItemParser

def print_item(item):
    print(f"Item Class: {item['item_class']}")
    print(f"Rarity: {item['rarity']}")
    print(f"Name: {item['name']}")
    print(f"Stack Size: {item['stack_size']}")
    print("--------")

# Test magic items
magic_data = """Item Class: Belts
Rarity: Magic
Innovative Plate Belt of Symbolism
--------
Charm Slots: 2 (augmented)
--------
Requirements:
Level: 44
--------
Item Level: 81
--------
+107 to Armour (implicit)
--------
25% increased Charm Effect Duration
+1 Charm Slot

Item Class: Rings
Rarity: Magic
Deliberate Sapphire Ring
--------
Requirements:
Level: 20
--------
Item Level: 80
--------
+23% to Cold Resistance (implicit)
--------
+119 to Accuracy Rating"""

# Test rare/unique armor data
rare_data = """Item Class: Helmets
Rarity: Rare
Victory Star
Expert Hunter Hood
--------
Quality: +20% (augmented)
Evasion Rating: 588 (augmented)
--------
Requirements:
Level: 75
Dex: 139
--------
Sockets: S 
--------
Item Level: 77
--------
+12% to Fire Resistance (rune)
--------
+94 to Evasion Rating
36% increased Evasion Rating
+35 to maximum Life
40% increased Rarity of Items found
+23% to Cold Resistance
+36% to Lightning Resistance

Item Class: Boots
Rarity: Rare
Storm Stride
Advanced Embossed Boots
--------
Quality: +20% (augmented)
Evasion Rating: 239 (augmented)
--------
Requirements:
Level: 65
Dex: 88
--------
Sockets: S 
--------
Item Level: 83
--------
+7% to Chaos Resistance (rune)
--------
35% increased Movement Speed
+66 to Evasion Rating
+24 to maximum Life
+36% to Fire Resistance
+26% to Lightning Resistance
+36 to Stun Threshold

Item Class: Boots
Rarity: Rare
Storm Stride
Advanced Embossed Boots
--------
Quality: +20% (augmented)
Evasion Rating: 239 (augmented)
--------
Requirements:
Level: 65
Dex: 88
--------
Sockets: S 
--------
Item Level: 83
--------
+7% to Chaos Resistance (rune)
--------
35% increased Movement Speed
+66 to Evasion Rating
+24 to maximum Life
+36% to Fire Resistance
+26% to Lightning Resistance
+36 to Stun Threshold"""

# Create parser and test
parser = ItemParser()

print("Testing Magic Items:")
items = parser.parse_items(magic_data)
for item in items:
    print_item(item)

print("\nTesting Rare Items:")
items = parser.parse_items(rare_data)
for item in items:
    print_item(item)
