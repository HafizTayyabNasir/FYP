const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'app/inbox/page.js');
let content = fs.readFileSync(filePath, 'utf8');

// Replacements
content = content.replace(/bg-\[#0D1421\]/g, 'bg-slate-50 dark:bg-[#060518]');
content = content.replace(/border-l-accent-blue/g, 'border-l-[#6D5DF6] dark:border-l-[#A78BFA]');
content = content.replace(/bg-dark-card/g, 'bg-white dark:bg-white/[0.015]');
content = content.replace(/bg-\[#1E3A5F\]\/20/g, 'bg-slate-200/50 dark:bg-[#6D5DF6]/10');
content = content.replace(/border-\[#5B9BF5\]\/20/g, 'border-slate-300 dark:border-[#6D5DF6]/20');
content = content.replace(/bg-\[#1E3A5F\]/g, 'bg-slate-200 dark:bg-[#6D5DF6]/20');
content = content.replace(/border-accent-violet/g, 'border-[#6D5DF6] dark:border-[#A78BFA]');
content = content.replace(/hover:bg-accent-violet\/10/g, 'hover:bg-[#6D5DF6]/10 dark:hover:bg-[#A78BFA]/10');
content = content.replace(/text-\[#F0F4FF\]/g, 'text-slate-900 dark:text-white');

fs.writeFileSync(filePath, content, 'utf8');
console.log('Fixed inbox styling');
