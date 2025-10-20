#!/usr/bin/env python3
"""
Generate screenshots from template files and upload to Imgbox
"""
import os
import sys
import subprocess
from pathlib import Path
import json

# Install required packages
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "openpyxl", "python-docx", "Pillow", "pdf2image"], check=False)

from PIL import Image, ImageDraw, ImageFont
import openpyxl
from docx import Document

def generate_excel_screenshot(xlsx_path, output_path, max_width=800, max_height=600):
    """Generate screenshot from Excel file"""
    try:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        
        # Create image
        img = Image.new('RGB', (max_width, max_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font = ImageFont.load_default()
        
        # Draw cell contents
        y_offset = 10
        for row_idx, row in enumerate(ws.iter_rows(max_row=30, max_col=10), 1):
            if y_offset > max_height - 20:
                break
            x_offset = 10
            for cell in row:
                if x_offset > max_width - 100:
                    break
                value = str(cell.value) if cell.value is not None else ""
                if value and value != "None":
                    # Truncate long values
                    if len(value) > 20:
                        value = value[:17] + "..."
                    draw.text((x_offset, y_offset), value, fill='black', font=font)
                x_offset += 80
            y_offset += 18
        
        # Add border
        draw.rectangle([(0, 0), (max_width-1, max_height-1)], outline='gray', width=2)
        
        img.save(output_path, 'PNG')
        print(f"✅ Generated Excel screenshot: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error generating Excel screenshot for {xlsx_path}: {e}")
        return False

def generate_word_screenshot(docx_path, output_path, max_width=800, max_height=600):
    """Generate screenshot from Word file"""
    try:
        doc = Document(docx_path)
        
        # Create image
        img = Image.new('RGB', (max_width, max_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            font = ImageFont.load_default()
            title_font = font
        
        # Draw paragraphs
        y_offset = 20
        for para in doc.paragraphs[:25]:  # First 25 paragraphs
            if y_offset > max_height - 40:
                break
            text = para.text.strip()
            if text:
                # Wrap text
                words = text.split()
                line = ""
                for word in words:
                    test_line = line + word + " "
                    if len(test_line) > 80:
                        draw.text((20, y_offset), line, fill='black', font=font)
                        y_offset += 20
                        line = word + " "
                        if y_offset > max_height - 40:
                            break
                    else:
                        line = test_line
                if line and y_offset < max_height - 40:
                    draw.text((20, y_offset), line, fill='black', font=font)
                    y_offset += 25
        
        # Add border
        draw.rectangle([(0, 0), (max_width-1, max_height-1)], outline='gray', width=2)
        
        img.save(output_path, 'PNG')
        print(f"✅ Generated Word screenshot: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error generating Word screenshot for {docx_path}: {e}")
        return False

def main():
    templates_dir = Path("static/templates")
    output_dir = Path("generated_screenshots")
    output_dir.mkdir(exist_ok=True)
    
    print("Generating screenshots from template files...\n")
    
    # Process all template files
    for template_file in sorted(templates_dir.glob("*.xlsx")):
        output_file = output_dir / f"{template_file.stem}.png"
        generate_excel_screenshot(template_file, output_file)
    
    for template_file in sorted(templates_dir.glob("*.docx")):
        output_file = output_dir / f"{template_file.stem}.png"
        generate_word_screenshot(template_file, output_file)
    
    print(f"\n✅ Screenshot generation complete! Files saved to: {output_dir}")
    print(f"Total screenshots: {len(list(output_dir.glob('*.png')))}")

if __name__ == "__main__":
    main()
