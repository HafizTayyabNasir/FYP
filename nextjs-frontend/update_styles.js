const fs = require('fs');
const path = require('path');

const replacements = [
  { regex: /bg-\[#161D2F\]/g, replacement: 'bg-white dark:bg-white/[0.015]' },
  { regex: /border-\[rgba\(255,255,255,0\.07\)\]/g, replacement: 'border-slate-200/80 dark:border-white/[0.06]' },
  { regex: /border-\[rgba\(255,255,255,0\.09\)\]/g, replacement: 'border-slate-200 dark:border-white/[0.06]' },
  { regex: /border-\[rgba\(255,255,255,0\.12\)\]/g, replacement: 'border-slate-300 dark:border-white/[0.12]' },
  { regex: /text-text-main/g, replacement: 'text-slate-900 dark:text-white' },
  { regex: /text-text-muted/g, replacement: 'text-slate-500 dark:text-[#8E8BA3]' },
  { regex: /bg-\[#1A2236\]/g, replacement: 'bg-slate-50 dark:bg-white/[0.03]' },
  { regex: /bg-\[#0F1623\]/g, replacement: 'bg-slate-100 dark:bg-[#08061a]' },
  { regex: /bg-\[#13192A\]/g, replacement: 'bg-slate-50 dark:bg-white/[0.02]' },
  { regex: /bg-\[#161E30\]/g, replacement: 'bg-white dark:bg-white/[0.01]' },
  { regex: /text-text-heading/g, replacement: 'text-slate-900 dark:text-white' },
  { regex: /text-text-tableh/g, replacement: 'text-slate-400 dark:text-[#6B6890]' },
  { regex: /bg-\[#1C2438\]/g, replacement: 'bg-slate-100 dark:bg-white/[0.04]' },
  { regex: /text-accent-blue/g, replacement: 'text-[#6D5DF6] dark:text-[#A78BFA]' },
  { regex: /text-accent-violet/g, replacement: 'text-[#A78BFA]' },
  { regex: /bg-\[#1E2840\]/g, replacement: 'bg-[#6D5DF6]/10 dark:bg-[#A78BFA]/10' },
  { regex: /shadow-\[0_2px_12px_rgba\(0,0,0,0\.4\)\]/g, replacement: 'shadow-sm dark:shadow-none' },
  { regex: /hover:bg-\[#1A2236\]/g, replacement: 'hover:bg-slate-50 dark:hover:bg-white/[0.03]' },
  { regex: /hover:text-text-heading/g, replacement: 'hover:text-slate-900 dark:hover:text-white' },
  { regex: /hover:text-text-main/g, replacement: 'hover:text-slate-900 dark:hover:text-white' },
  { regex: /bg-accent-blue/g, replacement: 'bg-[#6D5DF6] dark:bg-[#6D5DF6]' },
  { regex: /hover:bg-accent-blue/g, replacement: 'hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4]' },
  { regex: /hover:bg-primary-500/g, replacement: 'hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4]' },
  { regex: /focus:border-accent-blue/g, replacement: 'focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]' },
  { regex: /bg-accent-blue\/90/g, replacement: 'bg-[#6D5DF6]/90 dark:bg-[#6D5DF6]/90' },
  { regex: /hover:text-primary-400/g, replacement: 'hover:text-[#5b4ee4] dark:hover:text-[#A78BFA]' },
  { regex: /border-accent-blue/g, replacement: 'border-[#6D5DF6] dark:border-[#A78BFA]' }
];

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      processDirectory(fullPath);
    } else if (fullPath.endsWith('.js') && !fullPath.includes('login') && !fullPath.includes('landing') && !fullPath.includes('PublicShell.js') && !fullPath.includes('AppShell.js') && !fullPath.includes('Sidebar.js') && !fullPath.includes('page.js') && !fullPath.includes('layout.js')) {
        // wait I want to process dashboard pages
    }
  }
}

// I'll manually define the files to process to be safe
const filesToProcess = [
  'app/dashboard/page.js',
  'app/businesses/page.js',
  'app/audits/page.js',
  'app/outreach/page.js',
  'app/campaigns/page.js',
  'app/inbox/page.js',
  'app/settings/page.js'
];

for (const relPath of filesToProcess) {
  const fullPath = path.join(__dirname, relPath);
  if (fs.existsSync(fullPath)) {
    let content = fs.readFileSync(fullPath, 'utf8');
    for (const rule of replacements) {
      content = content.replace(rule.regex, rule.replacement);
    }
    fs.writeFileSync(fullPath, content, 'utf8');
    console.log('Processed', relPath);
  } else {
    console.log('Not found', relPath);
  }
}
