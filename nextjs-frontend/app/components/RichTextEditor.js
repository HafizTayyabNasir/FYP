'use client';

import { useRef, useCallback, useState, useEffect } from 'react';

const FONT_SIZES = ['12px','14px','16px','18px','20px','24px','28px','32px'];
const FONT_FAMILIES = ['Default','Arial','Georgia','Times New Roman','Courier New','Verdana','Trebuchet MS'];
const COLORS = ['#000000','#434343','#666666','#999999','#FFFFFF','#E74C3C','#E67E22','#F1C40F','#2ECC71','#1ABC9C','#3498DB','#9B59B6','#6D5DF6','#E91E63'];

export default function RichTextEditor({ value, onChange, placeholder, minHeight = '320px' }) {
  const editorRef = useRef(null);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showBgPicker, setShowBgPicker] = useState(false);
  const [showFontSize, setShowFontSize] = useState(false);
  const [showFontFamily, setShowFontFamily] = useState(false);
  const [showLinkInput, setShowLinkInput] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');
  const savedSelection = useRef(null);

  useEffect(() => {
    if (editorRef.current && value && !editorRef.current.innerHTML) {
      editorRef.current.innerHTML = value;
    }
  }, [value]);

  const exec = useCallback((cmd, val = null) => {
    editorRef.current?.focus();
    document.execCommand(cmd, false, val);
    if (onChange) onChange(editorRef.current.innerHTML);
  }, [onChange]);

  const handleInput = useCallback(() => {
    if (onChange) onChange(editorRef.current.innerHTML);
  }, [onChange]);

  const setContent = useCallback((html) => {
    if (editorRef.current) {
      editorRef.current.innerHTML = html;
      if (onChange) onChange(html);
    }
  }, [onChange]);

  // Expose setContent via ref-like pattern
  useEffect(() => {
    if (editorRef.current) {
      editorRef.current._setContent = setContent;
    }
  }, [setContent]);

  const saveSelection = () => {
    const sel = window.getSelection();
    if (sel.rangeCount > 0) savedSelection.current = sel.getRangeAt(0);
  };

  const restoreSelection = () => {
    if (savedSelection.current) {
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(savedSelection.current);
    }
  };

  const insertLink = () => {
    restoreSelection();
    if (linkUrl) exec('createLink', linkUrl);
    setShowLinkInput(false);
    setLinkUrl('');
  };

  const closeAllPopups = () => {
    setShowColorPicker(false);
    setShowBgPicker(false);
    setShowFontSize(false);
    setShowFontFamily(false);
    setShowLinkInput(false);
  };

  const ToolBtn = ({ onClick, title, active, children }) => (
    <button type="button" onClick={onClick} title={title}
      className={`p-1.5 rounded hover:bg-slate-200 dark:hover:bg-white/10 transition-colors text-slate-600 dark:text-slate-300 ${active ? 'bg-slate-200 dark:bg-white/15 text-slate-900 dark:text-white' : ''}`}>
      {children}
    </button>
  );

  const Divider = () => <div className="w-px h-6 bg-slate-300 dark:bg-white/10 mx-0.5" />;

  return (
    <div className="border border-slate-200/80 dark:border-white/[0.06] rounded-lg overflow-hidden bg-white dark:bg-[#08061a]">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-0.5 px-2 py-1.5 border-b border-slate-200/80 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.03] relative">

        {/* Font Family */}
        <div className="relative">
          <button type="button" onClick={() => { closeAllPopups(); setShowFontFamily(!showFontFamily); }}
            className="px-2 py-1 text-xs rounded hover:bg-slate-200 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-white/10 min-w-[80px] text-left truncate">
            Font ▾
          </button>
          {showFontFamily && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-[#1a1830] border border-slate-200 dark:border-white/10 rounded-lg shadow-xl z-50 py-1 min-w-[160px]">
              {FONT_FAMILIES.map(f => (
                <button key={f} type="button" onClick={() => { exec('fontName', f === 'Default' ? '' : f); setShowFontFamily(false); }}
                  style={{ fontFamily: f === 'Default' ? 'inherit' : f }}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-slate-100 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300">{f}</button>
              ))}
            </div>
          )}
        </div>

        {/* Font Size */}
        <div className="relative">
          <button type="button" onClick={() => { closeAllPopups(); setShowFontSize(!showFontSize); }}
            className="px-2 py-1 text-xs rounded hover:bg-slate-200 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-white/10 min-w-[50px] text-left">
            Size ▾
          </button>
          {showFontSize && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-[#1a1830] border border-slate-200 dark:border-white/10 rounded-lg shadow-xl z-50 py-1">
              {FONT_SIZES.map(s => (
                <button key={s} type="button" onClick={() => { exec('fontSize', '7'); /* use span hack */ const els = editorRef.current.querySelectorAll('font[size="7"]'); els.forEach(el => { el.removeAttribute('size'); el.style.fontSize = s; }); setShowFontSize(false); }}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-slate-100 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300">{s}</button>
              ))}
            </div>
          )}
        </div>

        <Divider />

        {/* Bold, Italic, Underline, Strikethrough */}
        <ToolBtn onClick={() => exec('bold')} title="Bold (Ctrl+B)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg></ToolBtn>
        <ToolBtn onClick={() => exec('italic')} title="Italic (Ctrl+I)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg></ToolBtn>
        <ToolBtn onClick={() => exec('underline')} title="Underline (Ctrl+U)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/><line x1="4" y1="21" x2="20" y2="21"/></svg></ToolBtn>
        <ToolBtn onClick={() => exec('strikeThrough')} title="Strikethrough"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="4" y1="12" x2="20" y2="12"/><path d="M17.5 7.5A4 4 0 0 0 12 4a4 4 0 0 0-4 3.5"/><path d="M8 14a4 4 0 0 0 4 4 4 4 0 0 0 4-3"/></svg></ToolBtn>

        <Divider />

        {/* Text Color */}
        <div className="relative">
          <ToolBtn onClick={() => { closeAllPopups(); saveSelection(); setShowColorPicker(!showColorPicker); }} title="Text Color">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 3L4 19h3l2-4h6l2 4h3L12 3z"/><rect x="2" y="20" width="20" height="3" rx="1" fill="currentColor" opacity="0.3"/></svg>
          </ToolBtn>
          {showColorPicker && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-[#1a1830] border border-slate-200 dark:border-white/10 rounded-lg shadow-xl z-50 p-2 grid grid-cols-7 gap-1">
              {COLORS.map(c => (
                <button key={c} type="button" onClick={() => { restoreSelection(); exec('foreColor', c); setShowColorPicker(false); }}
                  className="w-6 h-6 rounded border border-slate-200 dark:border-white/20 hover:scale-110 transition-transform" style={{ backgroundColor: c }} />
              ))}
            </div>
          )}
        </div>

        {/* Highlight / Background Color */}
        <div className="relative">
          <ToolBtn onClick={() => { closeAllPopups(); saveSelection(); setShowBgPicker(!showBgPicker); }} title="Highlight Color">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="14" width="18" height="7" rx="1" fill="#F1C40F" stroke="none" opacity="0.4"/><path d="M9 3h6l-3 11-3-11z" strokeWidth="2.5"/></svg>
          </ToolBtn>
          {showBgPicker && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-[#1a1830] border border-slate-200 dark:border-white/10 rounded-lg shadow-xl z-50 p-2 grid grid-cols-7 gap-1">
              {['transparent','#FDECEA','#FEF3E2','#FFF9C4','#E8F5E9','#E0F7FA','#E3F2FD','#F3E5F5','#FCE4EC','#FFF3E0','#F1F8E9','#E0F2F1','#E8EAF6','#EDE7F6'].map(c => (
                <button key={c} type="button" onClick={() => { restoreSelection(); exec('hiliteColor', c); setShowBgPicker(false); }}
                  className="w-6 h-6 rounded border border-slate-200 dark:border-white/20 hover:scale-110 transition-transform" style={{ backgroundColor: c === 'transparent' ? '#fff' : c }}>
                  {c === 'transparent' && <span className="text-[10px] text-red-500">✕</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        <Divider />

        {/* Headings */}
        <ToolBtn onClick={() => exec('formatBlock', '<h1>')} title="Heading 1"><span className="text-xs font-bold">H1</span></ToolBtn>
        <ToolBtn onClick={() => exec('formatBlock', '<h2>')} title="Heading 2"><span className="text-xs font-bold">H2</span></ToolBtn>
        <ToolBtn onClick={() => exec('formatBlock', '<h3>')} title="Heading 3"><span className="text-xs font-bold">H3</span></ToolBtn>
        <ToolBtn onClick={() => exec('formatBlock', '<p>')} title="Normal text"><span className="text-xs">¶</span></ToolBtn>

        <Divider />

        {/* Lists */}
        <ToolBtn onClick={() => exec('insertUnorderedList')} title="Bullet List">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="9" y1="6" x2="20" y2="6"/><line x1="9" y1="12" x2="20" y2="12"/><line x1="9" y1="18" x2="20" y2="18"/><circle cx="5" cy="6" r="1.5" fill="currentColor"/><circle cx="5" cy="12" r="1.5" fill="currentColor"/><circle cx="5" cy="18" r="1.5" fill="currentColor"/></svg>
        </ToolBtn>
        <ToolBtn onClick={() => exec('insertOrderedList')} title="Numbered List">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="10" y1="6" x2="20" y2="6"/><line x1="10" y1="12" x2="20" y2="12"/><line x1="10" y1="18" x2="20" y2="18"/><text x="3" y="8" fontSize="8" fill="currentColor" stroke="none" fontWeight="bold">1</text><text x="3" y="14" fontSize="8" fill="currentColor" stroke="none" fontWeight="bold">2</text><text x="3" y="20" fontSize="8" fill="currentColor" stroke="none" fontWeight="bold">3</text></svg>
        </ToolBtn>

        <Divider />

        {/* Alignment */}
        <ToolBtn onClick={() => exec('justifyLeft')} title="Align Left">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>
        </ToolBtn>
        <ToolBtn onClick={() => exec('justifyCenter')} title="Align Center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
        </ToolBtn>
        <ToolBtn onClick={() => exec('justifyRight')} title="Align Right">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg>
        </ToolBtn>

        <Divider />

        {/* Indent / Outdent */}
        <ToolBtn onClick={() => exec('indent')} title="Increase Indent">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="3" y1="4" x2="21" y2="4"/><line x1="11" y1="9" x2="21" y2="9"/><line x1="11" y1="14" x2="21" y2="14"/><line x1="3" y1="19" x2="21" y2="19"/><polyline points="3 8 7 11.5 3 15"/></svg>
        </ToolBtn>
        <ToolBtn onClick={() => exec('outdent')} title="Decrease Indent">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="3" y1="4" x2="21" y2="4"/><line x1="11" y1="9" x2="21" y2="9"/><line x1="11" y1="14" x2="21" y2="14"/><line x1="3" y1="19" x2="21" y2="19"/><polyline points="7 8 3 11.5 7 15"/></svg>
        </ToolBtn>

        <Divider />

        {/* Link */}
        <div className="relative">
          <ToolBtn onClick={() => { closeAllPopups(); saveSelection(); setShowLinkInput(!showLinkInput); }} title="Insert Link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          </ToolBtn>
          {showLinkInput && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-[#1a1830] border border-slate-200 dark:border-white/10 rounded-lg shadow-xl z-50 p-3 flex gap-2 min-w-[280px]">
              <input value={linkUrl} onChange={e => setLinkUrl(e.target.value)} placeholder="https://..." onKeyDown={e => e.key === 'Enter' && insertLink()}
                className="flex-1 px-2 py-1.5 text-sm bg-slate-100 dark:bg-[#08061a] border border-slate-200 dark:border-white/10 rounded text-slate-900 dark:text-white" />
              <button type="button" onClick={insertLink} className="px-3 py-1.5 text-sm bg-[#6D5DF6] text-white rounded hover:bg-[#5b4ee4]">Add</button>
            </div>
          )}
        </div>

        {/* Unlink */}
        <ToolBtn onClick={() => exec('unlink')} title="Remove Link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" opacity="0.4"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" opacity="0.4"/><line x1="4" y1="4" x2="20" y2="20" strokeWidth="2" stroke="#E74C3C"/></svg>
        </ToolBtn>

        <Divider />

        {/* Horizontal Rule */}
        <ToolBtn onClick={() => exec('insertHorizontalRule')} title="Horizontal Line">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="3" y1="12" x2="21" y2="12"/></svg>
        </ToolBtn>

        {/* Clear Formatting */}
        <ToolBtn onClick={() => exec('removeFormat')} title="Clear Formatting">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M6 4h10l-4 16"/><line x1="4" y1="20" x2="20" y2="4" stroke="#E74C3C" strokeWidth="2"/></svg>
        </ToolBtn>

        {/* Undo / Redo */}
        <ToolBtn onClick={() => exec('undo')} title="Undo (Ctrl+Z)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
        </ToolBtn>
        <ToolBtn onClick={() => exec('redo')} title="Redo (Ctrl+Y)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"/></svg>
        </ToolBtn>
      </div>

      {/* Editor */}
      <div ref={editorRef} contentEditable suppressContentEditableWarning
        onInput={handleInput}
        onClick={closeAllPopups}
        className="px-4 py-3 text-slate-900 dark:text-white focus:outline-none prose dark:prose-invert max-w-none prose-headings:mt-2 prose-headings:mb-1 prose-p:my-1 prose-li:my-0"
        style={{ minHeight }}
        data-placeholder={placeholder || 'Start typing your email...'}
      />

      <style jsx>{`
        [contenteditable]:empty::before {
          content: attr(data-placeholder);
          color: #8E8BA3;
          pointer-events: none;
        }
        [contenteditable] h1 { font-size: 1.75rem; font-weight: 700; }
        [contenteditable] h2 { font-size: 1.4rem; font-weight: 600; }
        [contenteditable] h3 { font-size: 1.15rem; font-weight: 600; }
        [contenteditable] ul { list-style: disc; padding-left: 1.5rem; }
        [contenteditable] ol { list-style: decimal; padding-left: 1.5rem; }
        [contenteditable] a { color: #6D5DF6; text-decoration: underline; }
        [contenteditable] blockquote { border-left: 3px solid #6D5DF6; padding-left: 1rem; margin-left: 0; opacity: 0.85; }
      `}</style>
    </div>
  );
}
