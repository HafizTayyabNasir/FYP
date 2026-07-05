import glob
import re

files = glob.glob('app/templates/pages/*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix broken hover classes from previous string replacement
    content = re.sub(r'hover:\s*[\"\']', '"', content)
    content = content.replace('hover:animate-slide-up', 'animate-slide-up')
    content = content.replace('hover: group', 'group')
    content = content.replace('hover: ', ' ')
    content = content.replace('card mb-4 hover: animate-slide-up', 'card mb-4 animate-slide-up')

    # Remove generic text colors that are replaced with primary colors for branding but don't work well on dark mode
    content = content.replace('text-gray-800', 'text-text-main')
    content = content.replace('text-gray-900', 'text-text-main')
    content = content.replace('text-gray-600', 'text-text-muted')
    content = content.replace('text-gray-500', 'text-text-muted')

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
