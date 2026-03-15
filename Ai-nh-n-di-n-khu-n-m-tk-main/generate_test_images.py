#!/usr/bin/env python3
"""
Generate sample face images for testing batch upload.
Uses random faces from Generated Photos API or creates placeholder images.
"""

import os
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random


def create_placeholder_face(size: int = 256) -> Image.Image:
    """
    Create a simple placeholder face image.
    For real testing, replace with actual face images.
    """
    img = Image.new('RGB', (size, size), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    
    # Draw simple face
    face_color = (random.randint(150, 230), random.randint(100, 180), random.randint(80, 150))
    draw.ellipse([50, 40, 206, 220], fill=face_color, outline='black', width=2)
    
    # Eyes
    draw.ellipse([90, 100, 110, 120], fill='white', outline='black', width=1)
    draw.ellipse([146, 100, 166, 120], fill='white', outline='black', width=1)
    draw.ellipse([100, 105, 108, 113], fill='black')
    draw.ellipse([156, 105, 164, 113], fill='black')
    
    # Mouth
    draw.arc([100, 130, 160, 160], 0, 180, fill='black', width=2)
    
    # Background variation
    for _ in range(20):
        x = random.randint(0, size)
        y = random.randint(0, size)
        draw.point((x, y), fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
    
    return img


def generate_test_images(output_dir: str, count: int = 20, size: int = 256):
    """
    Generate test face images.
    
    Args:
        output_dir: Directory to save images
        count: Number of images to generate
        size: Image size (size x size pixels)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Generating {count} test images in {output_dir}")
    print(f"📏 Size: {size}x{size} pixels\n")
    
    for i in range(1, count + 1):
        img = create_placeholder_face(size)
        filename = f"test_face_{i:03d}.jpg"
        filepath = output_path / filename
        img.save(filepath, quality=85)
        print(f"  [{i:3d}/{count}] {filename}")
    
    print(f"\n✓ Generated {count} test images in {output_dir}")
    print(f"💡 Tip: Replace these with real face images for better testing")
    print(f"   Or download from: http://thispersondoesnotexist.com/")


def generate_metadata(image_dir: str, output_file: str = "metadata.json"):
    """
    Generate metadata file for batch register API.
    
    Args:
        image_dir: Directory containing images
        output_file: Output metadata file
    """
    import json
    from pathlib import Path
    
    image_path = Path(image_dir)
    images = sorted([f for f in image_path.iterdir() if f.suffix.lower() in {'.jpg', '.png', '.jpeg'}])
    
    if not images:
        print(f"❌ No images found in {image_dir}")
        return
    
    metadata = []
    names = [
        "Alice Johnson", "Bob Smith", "Carol White", "David Brown", "Emma Davis",
        "Frank Miller", "Grace Wilson", "Henry Moore", "Isabella Taylor", "Jack Anderson",
        "Karen Thomas", "Leo Jackson", "Mia White", "Nathan Harris", "Olivia Martin",
        "Peter Thompson", "Quinn Lee", "Rachel Green", "Samuel Blue", "Tina Red"
    ]
    
    for idx, img_path in enumerate(images, 1):
        person_id = f"person_{idx:03d}"
        name = names[(idx - 1) % len(names)]
        
        metadata.append({
            "person_id": person_id,
            "name": f"{name} #{idx}",
            "filename": img_path.name
        })
    
    # Save metadata
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Generated metadata for {len(metadata)} images")
    print(f"  Saved to: {output_file}")
    print(f"\n  Sample entries:")
    for item in metadata[:3]:
        print(f"    - {item['person_id']}: {item['name']} ({item['filename']})")
    if len(metadata) > 3:
        print(f"    ... and {len(metadata) - 3} more")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test images for batch upload")
    parser.add_argument("--count", type=int, default=50, help="Number of images to generate")
    parser.add_argument("--size", type=int, default=256, help="Image size in pixels")
    parser.add_argument("--output", default="test_images", help="Output directory")
    parser.add_argument("--metadata", action="store_true", help="Also generate metadata.json")
    
    args = parser.parse_args()
    
    # Generate images
    generate_test_images(args.output, args.count, args.size)
    
    # Generate metadata if requested
    if args.metadata:
        print()
        generate_metadata(args.output, "metadata.json")
