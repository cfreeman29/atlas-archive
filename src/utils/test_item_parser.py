from item_parser import ItemParser

def print_item(item):
    print(f"Item Class: {item['item_class']}")
    print(f"Rarity: {item['rarity']}")
    print(f"Name: {item['name']}")
    print(f"Stack Size: {item['stack_size']}")
    print("--------")

# Test gem data
gem_data = """Item Class: Gems
Rarity: Currency
Uncut Skill Gem
--------
Level: 19
--------
Item Level: 19
--------
Creates a Skill Gem or Level an existing gem to level 19
--------
Right Click to engrave a Skill Gem.

Item Class: Gems
Rarity: Currency
Uncut Spirit Gem
--------
Level: 19
--------
Item Level: 19
--------
Creates a Persistent Buff Skill Gem or Level an existing gem to Level 19
--------
Right Click to engrave a Persistent Buff Skill Gem.

Item Class: Gems
Rarity: Currency
Uncut Spirit Gem
--------
Level: 19
--------
Item Level: 19
--------
Creates a Persistent Buff Skill Gem or Level an existing gem to Level 19
--------
Right Click to engrave a Persistent Buff Skill Gem.

Item Class: Gems
Rarity: Currency
Uncut Support Gem
--------
Level: 3
--------
Item Level: 3
--------
Creates a Support Gem up to level 3
--------
Right Click to engrave a Support Gem."""

# Test trials data
trials_data = """Item Class: Inscribed Ultimatum
Rarity: Currency
Inscribed Ultimatum
--------
Area Level: 80
Number of Trials: 10
--------
Item Level: 80
--------
Mortals spend their lives wondering which
fate shall be theirs. Chaos takes amusement
in knowing the answer: all of them.
--------
Take this item to The Temple of Chaos to participate in a Trial of Chaos.

Item Class: Trial Coins
Rarity: Currency
Djinn Barya
--------
Area Level: 80
Number of Trials: 4
--------
Item Level: 80
--------
"Take me to the Trial of the Sekhemas.
I will serve."
--------
Take this item to the Relic Altar at the Trial of the Sekhemas."""

# Test pinnacle key data
pinnacle_key_data = """Item Class: Pinnacle Keys
Rarity: Currency
Weathered Crisis Fragment
--------
Pictographs seem to convey a dire warning.
--------
Can be placed in a door in The Burning Monolith.

Item Class: Pinnacle Keys
Rarity: Currency
Ancient Crisis Fragment
--------
A carved piece of something older than the Vaal.
--------
Can be placed in a door in The Burning Monolith."""

# Test tablet data
tablet_data = """Item Class: Tablet
Rarity: Magic
Teeming Precursor Tablet of the Nemesis
--------
Item Level: 79
--------
5 Maps in Range are Irradiated (implicit)
--------
19% increased Magic Monsters in your Maps
Rare Monsters in your Maps have a 29% chance to have an additional Modifier
--------
Can be used in a completed Tower on your Atlas to influence surrounding Maps. Tablets are consumed once placed into a Tower.

Item Class: Tablet
Rarity: Normal
Overseer Precursor Tablet
--------
Item Level: 82
--------
Up to 3 Maps in Range contain Bosses (implicit)
--------
Can be used in a completed Tower on your Atlas to influence surrounding Maps. Tablets are consumed once placed into a Tower.

Item Class: Tablet
Rarity: Magic
Bountiful Delirium Precursor Tablet of Persecution
--------
Item Level: 79
--------
9 Maps in Range contain Mirrors of Delirium (implicit)
--------
Delirium Monsters in your Maps have 9% increased Pack Size
10% increased Gold found in your Maps
--------
Can be used in a completed Tower on your Atlas to influence surrounding Maps. Tablets are consumed once placed into a Tower.

Item Class: Tablet
Rarity: Magic
Teeming Ritual Precursor Tablet of the Foundling
--------
Item Level: 81
--------
9 Maps in Range contain Ritual Altars (implicit)
--------
23% increased Magic Monsters in your Maps
Revived Monsters from Ritual Altars in your Maps have 20% increased chance to be Magic
--------
Can be used in a completed Tower on your Atlas to influence surrounding Maps. Tablets are consumed once placed into a Tower.

Item Class: Tablet
Rarity: Magic
Teeming Breach Precursor Tablet of the Invasion
--------
Item Level: 80
--------
5 Maps in Range contain Breaches (implicit)
--------
Breaches in your Maps have 6% increased Monster density
15% increased Magic Monsters in your Maps
--------
Can be used in a completed Tower on your Atlas to influence surrounding Maps. Tablets are consumed once placed into a Tower."""

# Test relic data
relic_data = """Item Class: Relics
Rarity: Magic
Enduring Urn Relic of Worth
--------
Item Level: 69
--------
12% increased maximum Life
+10% to Honour Resistance
--------
Place this item on the Relic Altar at the start of the Trial of the Sekhemas"""

# Test jewel data
jewel_data = """Item Class: Jewels
Rarity: Rare
Luminous Stone
Emerald
--------
Item Level: 82
--------
5% increased Flask Effect Duration
Damage Penetrates 8% Lightning Resistance
Herald Skills deal 21% increased Damage
11% increased Daze Buildup
--------
Place into an allocated Jewel Socket on the Passive Skill Tree. Right click to remove from the Socket.

Item Class: Jewels
Rarity: Magic
Chaotic Sapphire of Glaciers
--------
Item Level: 81
--------
9% increased Chaos Damage
15% increased Freeze Buildup with Quarterstaves
--------
Place into an allocated Jewel Socket on the Passive Skill Tree. Right click to remove from the Socket."""

# Test amulet data
amulet_data = """Item Class: Amulets
Rarity: Rare
Vortex Beads
Lunar Amulet
--------
Requirements:
Level: 56
--------
Item Level: 81
--------
+26 to maximum Energy Shield (implicit)
--------
41% increased Armour
23% increased Rarity of Items found
+13% to Fire Resistance
+9% to Cold Resistance

Item Class: Amulets
Rarity: Rare
Blood Beads
Gold Amulet
--------
Requirements:
Level: 59
--------
Item Level: 81
--------
19% increased Rarity of Items found (implicit)
--------
18% increased Armour
+71 to maximum Energy Shield
+114 to maximum Life
13% increased Rarity of Items found
+39% to Fire Resistance
18% increased Mana Regeneration Rate"""

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

# Test omen data
omen_data = """Item Class: Omen
Rarity: Currency
Omen of Refreshment
--------
While this item is active in your inventory will
fully recover your flask and charm charges when you reach Low Life
--------
Right click this item in your inventory to set it to be active. This item is consumed when triggered. Only one Omen can be triggered from combat in each instance."""

# Test weapon data
weapon_data = """Item Class: Wands
Rarity: Unique
Sanguine Diviner
Bone Wand
--------
Requirements:
Level: 78
Int: 178
--------
Item Level: 81
--------
98% increased Spell Damage
Gain 12 Life per Enemy Killed
25% chance to inflict Bleeding on Hit
25% of Spell Mana Cost Converted to Life Cost
--------
One way or another, it will find what it seeks.

Item Class: Two Hand Maces
Rarity: Unique
Chober Chaber
Leaden Greathammer
--------
Physical Damage: 126-170 (augmented)
Critical Hit Chance: 10.00% (augmented)
Attacks per Second: 1.10
--------
Requirements:
Level: 33
Str: 76 (unmet)
Int: 100 (augmented)
--------
Item Level: 77
--------
+100 Intelligence Requirement
118% increased Physical Damage
+95 to maximum Mana
+5% to Critical Hit Chance
Increases and Reductions to Minion Damage also affect you
--------
The faithful may continue to serve, even after death.

Item Class: Bows
Rarity: Unique
Splinterheart
Recurve Bow
--------
Physical Damage: 38-78 (augmented)
Critical Hit Chance: 5.00%
Attacks per Second: 1.10
--------
Requirements:
Level: 16
Dex: 38
--------
Item Level: 80
--------
150% increased Physical Damage
+50 to Accuracy Rating
20% increased Projectile Speed
Projectiles Split towards +2 targets
--------
The forests of the Vastiri held many secrets
mystical and dark. Men learned not to wander,
lest they return with a strange new purpose.

Item Class: Staves
Rarity: Unique
Taryn's Shiver
Gelid Staff
--------
Requirements:
Level: 78
Int: 178
--------
Item Level: 79
--------
100% increased Cold Damage
13% increased Cast Speed
100% increased Freeze Buildup
Enemies Frozen by you take 50% increased Damage
--------
Shed by the winged beast of night,
A scaly frost-encrusted thorn.
All who feel its wintry light
Shiver in pain at the frozen dawn.

Item Class: Quivers
Rarity: Unique
Blackgleam
Fire Quiver
--------
Requirements:
Level: 8
--------
Item Level: 81
--------
Adds 3 to 5 Fire damage to Attacks (implicit)
--------
Adds 3 to 8 Fire damage to Attacks
+47 to maximum Mana
50% increased chance to Ignite
Projectiles Pierce all Ignited enemies
Attacks Gain 7% of Damage as Extra Fire Damage
--------
Molten feathers, veiled spark,
Hissing arrows from the dark.

Item Class: Shields
Rarity: Unique
Doomgate
Braced Tower Shield
--------
Block chance: 46% (augmented)
Armour: 101 (augmented)
--------
Requirements:
Level: 12
Str: 23
--------
Item Level: 70
--------
80% increased Block chance
147% increased Armour
You take 20% of damage from Blocked Hits
Enemies are Culled on Block
--------
Welcome to Wraeclast.

Item Class: Crossbows
Rarity: Unique
Rampart Raptor
Tense Crossbow
--------
Physical Damage: 10-19 (augmented)
Critical Hit Chance: 5.00%
Attacks per Second: 2.24 (augmented)
Reload Time: 1.21 (augmented)
--------
Item Level: 74
--------
23% increased Bolt Speed (implicit)
--------
49% increased Physical Damage
40% increased Attack Speed
100% chance to not consume a bolt if you've Reloaded Recently
30% reduced Reload Speed
--------
"His approach to the gate was met with sounding trumpets
and an unfurling of banners. He never saw it coming."
- anonymous Brotherhood of Silence report

Item Class: Foci
Rarity: Unique
The Eternal Spark
Crystal Focus
--------
Energy Shield: 47 (augmented)
--------
Requirements:
Level: 26
Int: 49
--------
Item Level: 76
--------
68% increased Energy Shield
+5% to Maximum Lightning Resistance
+26% to Lightning Resistance
50% increased Mana Regeneration Rate while stationary
--------
A flash of blue, a stormcloud's kiss,
her motionless dance the pulse of bliss

Item Class: Sceptres
Rarity: Unique
The Dark Defiler
Rattling Sceptre
--------
Spirit: 100
--------
Requirements:
Level: 78
Str: 54 (unmet)
Int: 138
--------
Item Level: 80
--------
+30 to maximum Mana
+6 to Intelligence
15% increased Mana Regeneration Rate
Gain 5% of Damage as Chaos Damage per Undead Minion
--------
Rare is the Necromancer who leads
his undead armies from the front.

Item Class: Quarterstaves
Rarity: Unique
The Sentry
Gothic Quarterstaff
--------
Physical Damage: 16-26
Fire Damage: 8-20 (augmented)
Critical Hit Chance: 11.50%
Attacks per Second: 1.40
--------
Requirements:
Level: 11
Dex: 22
Int: 11
--------
Item Level: 81
--------
Adds 8 to 20 Fire Damage
+20% to Fire Resistance
100% increased chance to Ignite
30% increased Light Radius
--------
The night Draven attacked,
Erian was asleep at his post."""

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

print("\nTesting Weapon Items:")
items = parser.parse_items(weapon_data)
for item in items:
    print_item(item)

print("\nTesting Omen Items:")
items = parser.parse_items(omen_data)
for item in items:
    print_item(item)

print("\nTesting Jewel Items:")
items = parser.parse_items(jewel_data)
for item in items:
    print_item(item)

print("\nTesting Relic Items:")
items = parser.parse_items(relic_data)
for item in items:
    print_item(item)

print("\nTesting Tablet Items:")
items = parser.parse_items(tablet_data)
for item in items:
    print_item(item)

print("\nTesting Pinnacle Key Items:")
items = parser.parse_items(pinnacle_key_data)
for item in items:
    print_item(item)

print("\nTesting Trials Items:")
items = parser.parse_items(trials_data)
for item in items:
    print_item(item)

print("\nTesting Gem Items:")
items = parser.parse_items(gem_data)
for item in items:
    print_item(item)

print("\nTesting Amulet Items:")
items = parser.parse_items(amulet_data)
for item in items:
    print_item(item)

# Test socketable data
socketable_data = """Item Class: Socketable
Rarity: Currency
Glacial Rune
--------
Stack Size: 10/10
--------
Martial Weapon: Adds 6 to 10 Cold Damage
Armour: +12% to Cold Resistance
--------
Place into an empty Rune Socket in a Martial Weapon or Armour to apply its effect to that item. Once socketed it cannot be removed.
Shift click to unstack.

Item Class: Socketable
Rarity: Currency
Soul Core of Citaqualotl
--------
Stack Size: 1/10
--------
Martial Weapon: 30% increased Elemental Damage with Attacks
Armour: +5% to all Elemental Resistances
--------
Place into an empty Rune Socket in a Martial Weapon or Armour to apply its effect to that item. Once socketed it cannot be removed."""

print("\nTesting Socketable Items:")
items = parser.parse_items(socketable_data)
for item in items:
    print_item(item)

# Test flask data
flask_data = """Item Class: Life Flasks
Rarity: Magic
Concentrated Ultimate Life Flask of the Surgeon
--------
Quality: +20% (augmented)
Recovers 1855 (augmented) Life over 3 Seconds
Consumes 10 of 75 Charges on use
Currently has 75 Charges
--------
Requirements:
Level: 60
--------
Item Level: 60
--------
68% increased Amount Recovered
35% Chance to gain a Charge when you Kill an Enemy
--------
Right click to drink. Can only hold charges while in belt. Refill at Wells or by killing monsters.

Item Class: Mana Flasks
Rarity: Magic
Concentrated Ultimate Mana Flask of the Abundant
--------
Quality: +20% (augmented)
Recovers 621 (augmented) Mana over 3 Seconds
Consumes 10 of 118 (augmented) Charges on use
Currently has 118 Charges
--------
Requirements:
Level: 60
--------
Item Level: 66
--------
67% increased Amount Recovered
58% increased Charges
--------
Right click to drink. Can only hold charges while in belt. Refill at Wells or by killing monsters."""

print("\nTesting Flask Items:")
items = parser.parse_items(flask_data)
for item in items:
    print_item(item)

# Test charm data
charm_data = """Item Class: Charms
Rarity: Magic
Analyst's Thawing Charm of the Medic
--------
Lasts 3.70 (augmented) Seconds
Consumes 80 of 80 Charges on use
Currently has 0 Charges
Grants Immunity to Freeze
--------
Requirements:
Level: 16
--------
Item Level: 49
--------
Used when you become Frozen (implicit)
--------
23% increased Duration
22% Chance to gain a Charge when you Kill an Enemy
--------
Used automatically when condition is met. Can only hold charges while in belt. Refill at Wells or by killing monsters.

Item Class: Charms
Rarity: Magic
Analyst's Golden Charm of the Bountiful
--------
Lasts 1.20 (augmented) Seconds
Consumes 80 of 120 (augmented) Charges on use
Currently has 120 Charges
20% increased Rarity of Items found
--------
Requirements:
Level: 50
--------
Item Level: 79
--------
Used when you Kill a Rare or Unique Enemy (implicit)
--------
24% increased Duration
51% increased Charges
--------
Used automatically when condition is met. Can only hold charges while in belt. Refill at Wells or by killing monsters.
--------
Corrupted"""

print("\nTesting Charm Items:")
items = parser.parse_items(charm_data)
for item in items:
    print_item(item)
