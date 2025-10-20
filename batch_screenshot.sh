#!/bin/bash
# Batch convert templates to screenshots
# Excel: landscape, Word: portrait

mkdir -p proper_screenshots
cd static/templates

echo "Converting templates to images..."
count=0

for file in *.xlsx *.docx; do
    if [ -f "$file" ]; then
        basename="${file%.*}"
        echo "Processing: $file"
        
        # Convert to PDF
        libreoffice --headless --convert-to pdf --outdir /tmp "$file" 2>/dev/null
        
        # Convert PDF to PNG
        if [ -f "/tmp/$basename.pdf" ]; then
            convert -density 150 -quality 90 -background white -alpha remove "/tmp/$basename.pdf[0]" "../../proper_screenshots/$basename.png" 2>/dev/null
            
            if [ -f "../../proper_screenshots/$basename.png" ]; then
                echo "✅ Created: $basename.png"
                ((count++))
            fi
            
            rm "/tmp/$basename.pdf"
        fi
    fi
done

echo ""
echo "========================================="
echo "✅ Generated $count screenshots"
echo "📁 Location: proper_screenshots/"
echo "========================================="

