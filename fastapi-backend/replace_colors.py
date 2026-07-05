import os
import glob

# Paths to process
templates_dir = 'app/templates/pages'
files = glob.glob(f'{templates_dir}/*.html')

replacements = {
    'class="text-text-muted text-sm italic">Not audited': 'class="badge badge-muted">Not audited',
    'text-gray-400 bg-gray-100': 'text-text-muted bg-[#2A3347]',
    'text-gray-400': 'text-text-muted',
    'text-gray-500': 'text-text-muted',
    'text-primary-700 bg-primary-50 hover:bg-primary-100': 'text-accent-blue bg-accent-blue/10 hover:bg-accent-blue/20',
    'text-orange-500 bg-orange-500/10 hover:bg-orange-500/20': 'text-accent-amber bg-accent-amber/10 hover:bg-accent-amber/20',
    'text-purple-500 bg-purple-500/10 hover:bg-purple-500/20': 'text-accent-violet bg-accent-violet/10 hover:bg-accent-violet/20',
    'text-primary-500 bg-primary-500/10 hover:bg-primary-500/20': 'text-accent-blue bg-accent-blue/10 hover:bg-accent-blue/20',
    'text-primary-500': 'text-accent-blue',
    'text-primary-600': 'text-accent-blue',
    'text-primary-700': 'text-accent-blue',
    'text-green-500': 'text-[#8BA1C1]',
    'text-blue-500': 'text-accent-blue',
    'text-purple-500': 'text-accent-violet',
    'text-orange-500': 'text-accent-amber',
    'text-yellow-500': 'text-accent-amber',
    'bg-primary-50': 'bg-[#1E2840]',
    'bg-primary-100': 'bg-accent-blue/20',
    'bg-primary-500': 'bg-accent-blue',
    'border-primary-500': 'border-accent-blue',
    'ring-primary-500': 'ring-accent-blue',
    'text-emerald-500': 'text-[#8BA1C1]', 
    'bg-emerald-500': 'bg-[#8BA1C1]',
}

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Replacements complete.')
