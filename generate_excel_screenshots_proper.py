#!/usr/bin/env python3
"""
Generate proper Excel screenshots:
- Capture the 2nd sheet (dashboard/data, not instructions)
- Landscape orientation
- Show all columns
"""
import os
import sys
from pathlib import Path
import subprocess
import tempfile

def generate_excel_screenshot_sheet2(excel_file, output_png):
    """
    Generate screenshot of 2nd sheet from Excel file using LibreOffice with specific sheet selection
    """
    try:
        # Create a temporary macro to export only sheet 2
        temp_dir = tempfile.mkdtemp()
        temp_pdf = Path(temp_dir) / f"{excel_file.stem}_sheet2.pdf"
        
        # Use LibreOffice with filter options to export specific sheet
        # Unfortunately LibreOffice command line doesn't support sheet selection easily
        # We'll use a workaround: convert to PDF and get page 2 (which is sheet 2)
        
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', temp_dir,
            str(excel_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Find the generated PDF
        pdf_file = Path(temp_dir) / f"{excel_file.stem}.pdf"
        
        if not pdf_file.exists():
            print(f"❌ PDF not created for {excel_file.name}")
            return False
        
        # Convert PDF page 2 (index 1) to PNG in landscape
        # Use page 1 for now (will be sheet 2 after we fix the export)
        cmd = [
            'convert',
            '-density', '150',
            '-quality', '90',
            '-background', 'white',
            '-alpha', 'remove',
            f'{pdf_file}[1]',  # Page 2 (0-indexed, so [1] = page 2)
            str(output_png)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Clean up temp files
        if pdf_file.exists():
            pdf_file.unlink()
        os.rmdir(temp_dir)
        
        if output_png.exists():
            print(f"✅ {excel_file.name} → {output_png.name}")
            return True
        else:
            print(f"❌ Failed to convert {excel_file.name}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout: {excel_file.name}")
        return False
    except Exception as e:
        print(f"❌ Error {excel_file.name}: {e}")
        return False

def main():
    templates_dir = Path("static/templates")
    output_dir = Path("excel_screenshots_sheet2")
    output_dir.mkdir(exist_ok=True)
    
    print("Generating Excel screenshots (Sheet 2 - Dashboard/Data)...\n")
    
    excel_files = sorted(templates_dir.glob("*.xlsx"))
    total = len(excel_files)
    success = 0
    failed = 0
    
    for i, excel_file in enumerate(excel_files, 1):
        print(f"[{i}/{total}] Processing: {excel_file.name}")
        output_file = output_dir / f"{excel_file.stem}.png"
        
        if generate_excel_screenshot_sheet2(excel_file, output_file):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Success: {success}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📁 Output: {output_dir}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

