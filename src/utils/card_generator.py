from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from .resource_path import get_resource_path

def generate_map_run_card(run_data, save_path):
    """Generate a styled map run card image."""
    # Create base image with margins
    card_width = 1000
    card_height = 600
    margin = 20
    width = card_width + 2*margin
    height = card_height + 2*margin
    background_color = (15, 15, 15)  # Outer background
    
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Draw card background with 3D effect
    # Bottom shadow
    draw.rectangle(
        [(margin-2, margin-2), (width-margin+2, height-margin+2)],
        fill=(10, 10, 10)
    )
    
    # Main card background
    draw.rectangle(
        [(margin, margin), (width-margin, height-margin)],
        fill=(18, 18, 18)
    )
    
    # Top highlight
    draw.line(
        [(margin, margin), (width-margin, margin)],
        fill=(30, 30, 30), width=1
    )
    draw.line(
        [(margin, margin), (margin, height-margin)],
        fill=(30, 30, 30), width=1
    )
    
    try:
        # Load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)  # App name
            map_font = ImageFont.truetype("arial.ttf", 24)    # Map name
            header_font = ImageFont.truetype("arial.ttf", 18)  # Section headers
            normal_font = ImageFont.truetype("arial.ttf", 16)  # Items
            char_font = ImageFont.truetype("arial.ttf", 12)  # Items
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
        
        # Header with logo (inside margins)
        logo = Image.open(get_resource_path('src/images/app/icon.png'))
        logo = logo.resize((48, 48), Image.Resampling.LANCZOS)
        logo_x = margin + 20
        logo_y = margin + 20
        img.paste(logo, (logo_x, logo_y), logo if 'A' in logo.getbands() else None)
        draw.text((logo_x + 60, logo_y + 5), "Atlas Archive", fill=(255, 255, 255), font=title_font)
        
        # Draw divider
        draw.line(
            [(margin, margin + 90), (width-margin, margin + 90)],
            fill=(40, 40, 40), width=2
        )
        
        # Info section
        info_y = margin + 110
        info_x = margin + 20
        
        # Status in green/red
        status_text = "Complete" if run_data['completion_status'] == 'complete' else "RIP"
        status_color = (0, 255, 0) if run_data['completion_status'] == 'complete' else (255, 0, 0)
        
        # First line: Map name, status, duration
        map_text = f"{run_data['map_name']} (Level {run_data['map_level']})"
        duration_mins = run_data['duration'] // 60
        duration_secs = run_data['duration'] % 60
        
        # Calculate text widths for proper spacing
        map_width = draw.textlength(map_text, font=map_font)
        status_width = draw.textlength(status_text, font=header_font)
        
        # Draw map name in red
        draw.text((info_x, info_y), map_text, fill=(255, 50, 50), font=map_font)
        
        # Draw status after map name with spacing
        status_x = info_x + map_width + 50
        draw.text((status_x, info_y + 4), status_text, fill=status_color, font=header_font)
        
        # Draw duration after status
        duration_x = status_x + status_width + 50
        draw.text((duration_x, info_y + 4), f"Duration: {duration_mins:02d}:{duration_secs:02d}", 
                 fill=(200, 200, 200), font=header_font)
        
        # Second line: Boss and time
        info_y += 30  # Reduced spacing
        boss_text = "Single Boss" if run_data['boss_count'] == 1 else "Twin Boss" if run_data['boss_count'] == 2 else "No Boss"
        start_time = datetime.fromisoformat(run_data['start_time'])
        draw.text((info_x, info_y), f"{boss_text} | {start_time.strftime('%Y-%m-%d %H:%M:%S')}", 
                 fill=(150, 150, 150), font=normal_font)
        
        # Character info (if available)
        if run_data.get('character_id') and run_data.get('db'):
            char = run_data['db'].get_character(run_data['character_id'])
            if char:
                # Draw character name and build info
                char_x = width - margin - 400  # Further left for longer text
                char_y = margin + 40  # Higher up, near the logo
                
                # Character name
                char_text = f"{char['name']} (Level {char['level']} {char['class']}"
                if char['ascendancy']:
                    char_text += f" - {char['ascendancy']}"
                char_text += ")"
                draw.text((char_x, char_y), char_text, fill=(68, 255, 68), font=normal_font)
                
                # Build info
                if run_data.get('build_id'):
                    build = run_data['db'].get_build(run_data['build_id'])
                    if build:
                        build_y = char_y + normal_font.size + 5  # Add some spacing
                        build_text = f"Build: {build['name']} ({build['url']})"
                        draw.text((char_x, build_y), build_text, fill=(150, 150, 150), font=char_font)

        # Mechanics section (right aligned with proper spacing)
        mech_x = width - margin - 150  # Closer to right edge
        mech_title_y = margin + 140  # Moved down slightly to accommodate character info
        draw.text((mech_x, mech_title_y), "Mechanics:", fill=(255, 255, 255), font=header_font)
        
        # Only show active mechanics
        active_mechanics = []
        if run_data.get('has_breach', False):
            active_mechanics.append(('breach', run_data.get('breach_count', 0)))
        if run_data.get('has_delirium', False):
            active_mechanics.append(('delirium', None))
        if run_data.get('has_expedition', False):
            active_mechanics.append(('expedition', None))
        if run_data.get('has_ritual', False):
            active_mechanics.append(('ritual', None))
        
        # Draw mechanics vertically (adjusted starting position)
        mech_y = mech_title_y + 35  # This maintains the same spacing from the "Mechanics:" text
        icon_size = 48  # Slightly smaller icons
        icon_spacing = 55  # Consistent spacing
        
        for mech, count in active_mechanics:
            icon = Image.open(get_resource_path(f'src/images/endgame-mech/{mech}.png'))
            icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            img.paste(icon, (mech_x, mech_y), icon if 'A' in icon.getbands() else None)
            
            if count:
                count_x = mech_x + icon_size + 5
                count_y = mech_y + (icon_size - header_font.size) // 2  # Vertically center count
                draw.text((count_x, count_y), f"x{count}", fill=(255, 255, 255), font=header_font)
            
            mech_y += icon_spacing
        
        # Items section
        items_y = 250
        
        # Draw dark panel (inside margins)
        draw.rectangle(
            [(margin, items_y), (width-margin, height-margin)],
            fill=(13, 13, 13)
        )
        
        # Calculate column positions
        col_width = (width - 2*margin) // 3
        col1_x = margin + 20
        col2_x = margin + col_width + 20
        col3_x = margin + 2*col_width + 20
        
        # Draw section headers
        header_y = items_y + 10
        draw.text((col1_x, header_y), "Currency", fill=(128, 128, 128), font=header_font)
        draw.text((col2_x, header_y), "Unique Items", fill=(128, 128, 128), font=header_font)
        draw.text((col3_x, header_y), "Other Items", fill=(128, 128, 128), font=header_font)
        
        # Group items
        currency_items = []
        unique_items = []
        other_items = []
        
        for item in run_data['items']:
            if (item['name'] != 'Unknown Item' and 
                not item['name'].startswith('Item Class:') and 
                not item['name'].startswith('Stack Size:') and 
                not item['name'].startswith('Rarity:')):
                name_parts = item['name'].rsplit('_', 1)
                display_name = name_parts[0]
                rarity = name_parts[1] if len(name_parts) > 1 else 'Normal'
                
                if item['name'].endswith('_Currency'):
                    currency_items.append((display_name, item['stack_size'], (170, 158, 130)))
                elif item['name'].endswith('_Unique'):
                    unique_items.append((display_name, item['stack_size'], (175, 96, 37)))
                else:
                    if item['name'].endswith('_pinkey'):
                        color = (255, 0, 0)
                    elif item['name'].endswith('_trials'):
                        color = (183, 65, 14)
                    elif item['name'].endswith('_gem'):
                        color = (192, 192, 192)
                    elif item['name'].endswith('_socket'):
                        color = (173, 216, 230)
                    else:
                        color = {
                            'Normal': (255, 255, 255),
                            'Magic': (136, 136, 255),
                            'Rare': (255, 255, 119)
                        }.get(rarity, (204, 204, 204))
                    other_items.append((display_name, item['stack_size'], color))
        
        # Draw items with dynamic font sizing
        def draw_items(items, start_x, start_y):
            if not items:
                return
            
            # Calculate available space
            available_height = height - margin - start_y - 80
            min_spacing = 4  # Minimum pixels between items
            
            # Calculate required font size
            base_size = 16
            while base_size > 8:  # Don't go smaller than 8pt
                try:
                    test_font = ImageFont.truetype("arial.ttf", base_size)
                    total_height = (test_font.size + min_spacing) * len(items)
                    if total_height <= available_height:
                        break
                    base_size -= 1
                except:
                    break
            
            # Create font with calculated size
            try:
                item_font = ImageFont.truetype("arial.ttf", base_size)
            except:
                item_font = normal_font
            
            # Calculate actual spacing to distribute items evenly
            item_spacing = (available_height - (item_font.size * len(items))) // (len(items) + 1)
            item_spacing = max(item_spacing, min_spacing)
            
            # Draw items
            y = start_y + 40
            for name, count, color in items:
                item_text = f"{name} x{count}"
                # Draw text with shadow
                draw.text((start_x+1, y+1), item_text, fill=(0, 0, 0), font=item_font)
                draw.text((start_x, y), item_text, fill=color, font=item_font)
                y += item_font.size + item_spacing
        
        # Draw items aligned with headers
        draw_items(currency_items, col1_x, items_y)
        draw_items(unique_items, col2_x, items_y)
        draw_items(other_items, col3_x, items_y)
        
        # Save the image
        img.save(save_path, 'PNG')
        return True
        
    except Exception as e:
        print(f"Error generating map run card: {e}")
        return False
