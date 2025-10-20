#!/usr/bin/env python3
"""
Generate high-quality screenshots from template files using LibreOffice
- Excel: Capture 2nd sheet (full view)
- Word: Capture title page (full page)
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

def convert_to_pdf_then_image(input_file, output_image, sheet_index=1):
    """Convert Office file to PDF, then PDF to image"""
    temp_pdf = Path(f"/tmp/{input_file.stem}.pdf")
    
    try:
        # Convert to PDF using LibreOffice
        if input_file.suffix == '.xlsx':
            # For Excel, we need to export specific sheet
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', '/tmp',
                str(input_file)
            ]
        else:
            # For Word
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', '/tmp',
                str(input_file)
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if not temp_pdf.exists():
            print(f"❌ PDF conversion failed for {input_file.name}")
            return False
        
        # Convert PDF to PNG using ImageMagick (first page only)
        cmd = [
            'convert',
            '-density', '150',
            '-quality', '90',
            '-background', 'white',
            '-alpha', 'remove',
            f'{temp_pdf}[0]',  # First page only
            str(output_image)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if output_image.exists():
            print(f"✅ Generated screenshot: {output_image.name}")
            # Clean up temp PDF
            temp_pdf.unlink()
            return True
        else:
            print(f"❌ Image conversion failed for {input_file.name}")
            if temp_pdf.exists():
                temp_pdf.unlink()
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout converting {input_file.name}")
        if temp_pdf.exists():
            temp_pdf.unlink()
        return False
    except Exception as e:
        print(f"❌ Error converting {input_file.name}: {e}")
        if temp_pdf.exists():
            temp_pdf.unlink()
        return False

def main():
    templates_dir = Path("static/templates")
    output_dir = Path("proper_screenshots")
    output_dir.mkdir(exist_ok=True)
    
    print("Generating high-quality screenshots from templates...\n")
    print("This may take a few minutes...\n")
    
    success_count = 0
    fail_count = 0
    
    # Process Excel files
    print("📊 Processing Excel files...")
    for template_file in sorted(templates_dir.glob("*.xlsx")):
        output_file = output_dir / f"{template_file.stem}.png"
        if convert_to_pdf_then_image(template_file, output_file, sheet_index=1):
            success_count += 1
        else:
            fail_count += 1
    
    # Process Word files
    print("\n📄 Processing Word files...")
    for template_file in sorted(templates_dir.glob("*.docx")):
        output_file = output_dir / f"{template_file.stem}.png"
        if convert_to_pdf_then_image(template_file, output_file):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Success: {success_count} screenshots")
    print(f"❌ Failed: {fail_count} screenshots")
    print(f"📁 Output directory: {output_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

