import re
import os
from pathlib import Path

def remove_icons_from_file(filepath):
    """Remove all FontAwesome icons and emojis from an HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Remove <i class="fas/fab/far ..."></i> tags completely
    content = re.sub(r'<i\s+class="fa[brs]\s+[^"]*"[^>]*></i>\s*', '', content)
    
    # Pattern 2: Remove emoji characters
    emoji_pattern = r'[🎯🚀💡📊✨🔒⚡💼📈🎨🔧⭐🌟💪🏆📱💻🎁🔥👥📝✅❌⚠️📢🎉🤝💰📉🗂️📅🔔🎓🌐🔍📎🖼️]'
    content = re.sub(emoji_pattern, '', content)
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    templates_dir = Path('/home/ubuntu/pmb_repo/templates')
    modified_files = []
    
    # Process all HTML files
    for html_file in templates_dir.rglob('*.html'):
        if remove_icons_from_file(html_file):
            modified_files.append(str(html_file))
            print(f"Modified: {html_file}")
    
    print(f"\n✓ Total files modified: {len(modified_files)}")
    
    # Save list of modified files
    with open('/home/ubuntu/modified_files.txt', 'w') as f:
        f.write('\n'.join(modified_files))

if __name__ == '__main__':
    main()
