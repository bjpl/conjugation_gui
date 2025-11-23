"""
Professional Icon Generator for Spanish Conjugation App
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a professional application icon"""
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # Create image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Professional color scheme
        primary_color = (41, 128, 185)  # Professional blue
        accent_color = (231, 76, 60)    # Spanish red accent
        text_color = (255, 255, 255)    # White text
        
        # Draw background circle
        margin = size // 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=primary_color,
            outline=accent_color,
            width=max(1, size // 32)
        )
        
        # Draw stylized "ES" for Spanish
        try:
            # Use a built-in font
            font_size = size // 3
            font = ImageFont.load_default()
            
            text = "ES"
            # Calculate text position to center it
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, font=font, fill=text_color)
            
        except Exception:
            # Fallback: draw simple geometric pattern
            center = size // 2
            inner_size = size // 4
            draw.rectangle(
                [center - inner_size//2, center - inner_size//2,
                 center + inner_size//2, center + inner_size//2],
                fill=text_color
            )
        
        # Save icon
        icon_path = f"src/resources/icon_{size}.png"
        img.save(icon_path, 'PNG')
        print(f"Created icon: {icon_path}")
    
    # Create ICO file for Windows
    try:
        # Load the largest PNG for ICO conversion
        img = Image.open("src/resources/icon_256.png")
        img.save("src/resources/app_icon.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("Created Windows ICO file: src/resources/app_icon.ico")
    except Exception as e:
        print(f"Could not create ICO file: {e}")

def create_splash_screen():
    """Create a professional splash screen"""
    width, height = 600, 400
    img = Image.new('RGB', (width, height), (52, 73, 94))  # Dark background
    draw = ImageDraw.Draw(img)
    
    # Professional gradient effect (simplified)
    for y in range(height):
        color_value = int(52 + (y / height) * 30)  # Gradient from dark to lighter
        draw.line([(0, y), (width, y)], fill=(color_value, color_value + 20, color_value + 40))
    
    # Title
    try:
        font = ImageFont.load_default()
        title = "Spanish Conjugation Trainer"
        subtitle = "Professional Language Learning Tool"
        version = "Version 2.0"
        
        # Center text
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        
        draw.text(
            ((width - title_width) // 2, height // 2 - 60),
            title,
            font=font,
            fill=(255, 255, 255)
        )
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        
        draw.text(
            ((width - subtitle_width) // 2, height // 2 - 20),
            subtitle,
            font=font,
            fill=(189, 195, 199)
        )
        
        version_bbox = draw.textbbox((0, 0), version, font=font)
        version_width = version_bbox[2] - version_bbox[0]
        
        draw.text(
            ((width - version_width) // 2, height // 2 + 20),
            version,
            font=font,
            fill=(149, 165, 166)
        )
        
    except Exception:
        pass
    
    img.save("src/resources/splash.png", 'PNG')
    print("Created splash screen: src/resources/splash.png")

if __name__ == "__main__":
    os.makedirs("src/resources", exist_ok=True)
    create_app_icon()
    create_splash_screen()