import os
import re

def convert_to_dark_mode(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Colors
    content = content.replace('bg-white', 'bg-dark-card border border-dark-border')
    content = content.replace('text-gray-800', 'text-text-main')
    content = content.replace('text-gray-900', 'text-text-main')
    content = content.replace('text-gray-700', 'text-text-muted')
    content = content.replace('text-gray-600', 'text-text-muted')
    content = content.replace('text-gray-500', 'text-text-muted')
    content = content.replace('text-gray-400', 'text-text-muted')
    content = content.replace('border-gray-200', 'border-dark-border')
    content = content.replace('border-gray-100', 'border-dark-border')
    content = content.replace('bg-gray-50', 'bg-dark-hover')
    content = content.replace('bg-gray-100', 'bg-dark-hover')
    content = content.replace('bg-gray-200', 'bg-dark-border')
    
    # Gradients & Shadows
    content = re.sub(r'bg-gradient-to-[a-z]+ ', '', content)
    content = re.sub(r'from-[a-z]+-\d+ ', '', content)
    content = re.sub(r'to-[a-z]+-\d+ ', '', content)
    content = re.sub(r'shadow-[a-z]+ ', '', content)
    content = content.replace('shadow-xl', '')
    content = content.replace('shadow-lg', '')
    content = content.replace('shadow-md', '')
    content = content.replace('shadow-sm', '')
    content = content.replace('shadow', '')
    content = content.replace('hover:shadow-xl', '')
    
    # Buttons and Badges
    content = content.replace('bg-green-50', 'bg-emerald-500/10')
    content = content.replace('text-green-600', 'text-emerald-500')
    content = content.replace('text-green-700', 'text-emerald-500')
    content = content.replace('bg-green-100', 'bg-emerald-500/20')
    
    content = content.replace('bg-amber-50', 'bg-amber-500/10')
    content = content.replace('text-amber-600', 'text-amber-500')
    content = content.replace('text-amber-700', 'text-amber-500')
    content = content.replace('bg-amber-100', 'bg-amber-500/20')

    content = content.replace('bg-red-50', 'bg-red-500/10')
    content = content.replace('text-red-600', 'text-red-500')
    content = content.replace('text-red-800', 'text-red-500')
    content = content.replace('bg-red-100', 'bg-red-500/20')

    content = content.replace('bg-blue-50', 'bg-primary-500/10')
    content = content.replace('text-blue-600', 'text-primary-500')
    content = content.replace('text-blue-700', 'text-primary-500')
    content = content.replace('bg-blue-100', 'bg-primary-500/20')
    
    content = content.replace('bg-purple-50', 'bg-purple-500/10')
    content = content.replace('text-purple-600', 'text-purple-500')
    content = content.replace('text-purple-700', 'text-purple-500')
    content = content.replace('bg-purple-100', 'bg-purple-500/20')

    content = content.replace('bg-orange-50', 'bg-orange-500/10')
    content = content.replace('text-orange-700', 'text-orange-500')
    content = content.replace('bg-orange-100', 'bg-orange-500/20')

    # Primary colors inside SVG wrappers
    content = content.replace('text-white', 'text-text-main')

    # Chart colors update for JS
    content = content.replace("Chart.defaults.color = '#666'", "Chart.defaults.color = '#94A3B8'; Chart.defaults.font.family = 'Inter';")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

files_to_convert = [
    r"d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend\app\templates\pages\businesses.html",
    r"d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend\app\templates\pages\audits.html",
    r"d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend\app\templates\pages\outreach.html",
    r"d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend\app\templates\pages\campaigns.html",
    r"d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend\app\templates\pages\inbox.html",
    r"d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend\app\templates\pages\settings.html"
]

for file in files_to_convert:
    if os.path.exists(file):
        convert_to_dark_mode(file)
        print(f"Converted: {file}")
    else:
        print(f"Not found: {file}")
