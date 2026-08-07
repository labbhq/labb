// Registered once per page — handles URL-change messages from any lbb preview iframe
if (!window.__lbbRendererSetup) {
  window.__lbbRendererSetup = true;
  window.addEventListener('message', (e) => {
    if (!e.data || e.data.type !== 'lbb:urlchange') return;
    const iframe = Array.from(document.querySelectorAll('iframe[data-lbb-bar]'))
      .find(f => { try { return f.contentWindow === e.source; } catch (_) { return false; } });
    if (!iframe) return;
    const bar = document.getElementById(iframe.dataset.lbbBar);
    if (!bar) return;
    const changed = bar.textContent !== e.data.path;
    bar.textContent = e.data.path;
    if (changed) {
      // Slow amber flash so a state change that updated the URL is noticeable.
      bar.classList.remove('lbb-url-flash');
      void bar.offsetWidth; // restart the animation
      bar.classList.add('lbb-url-flash');
    }
  });
}

// Preview-iframe loader. The real URL rides in data-lbb-src; we load it with
// location.replace() so it never pushes a browser-history entry — a JS-set
// iframe `src` does, so a page of previews would stack entries and the back
// button would unwind them (blanking iframes) instead of leaving the page.
// data-lbb-lazy defers the load until the frame scrolls into view.
if (!window.__lbbFrameLoader) {
  window.__lbbFrameLoader = true;

  const lbbLoadFrame = (frame) => {
    const url = frame.dataset.lbbSrc;
    if (!url) return;
    const target = new URL(url, location.href).href;
    // Compare against the frame's live location, not a one-shot flag: it may be
    // blank (initial load, or a hydration/morph reset) OR still showing the
    // previous block (a tab switch morphs data-lbb-src in place) — both must
    // (re)load. A cross-origin read throwing means it already navigated away, so
    // leave it. location.replace() loads without a browser-history entry.
    let href;
    try { href = frame.contentWindow.location.href; }
    catch (_) { return; }
    if (href === target) return;
    try { frame.contentWindow.location.replace(url); }
    catch (_) { frame.src = url; }
  };

  // Catalogue-only "start here" hint: if the block marked its primary interactive
  // element with data-lbb-start, pulse a ring around it a few times so a new
  // reader knows where to begin. Injected into the (same-origin) preview doc, so
  // installed blocks — which never run in this renderer — stay clean.
  const lbbAddStartPing = (frame) => {
    let doc;
    try { doc = frame.contentDocument; } catch (_) { return; }
    if (!doc) return;
    const el = doc.querySelector('[data-lbb-start]');
    if (!el || el.dataset.lbbPinging) return;
    el.dataset.lbbPinging = '1';
    if (!doc.getElementById('lbb-ping-style')) {
      const st = doc.createElement('style');
      st.id = 'lbb-ping-style';
      st.textContent =
        '@keyframes lbbstartglow{0%,100%{box-shadow:0 0 0 1px color-mix(in oklab,var(--color-warning) 35%,transparent),0 0 6px 1px color-mix(in oklab,var(--color-warning) 25%,transparent)}50%{box-shadow:0 0 0 2px color-mix(in oklab,var(--color-warning) 55%,transparent),0 0 12px 2px color-mix(in oklab,var(--color-warning) 40%,transparent)}}' +
        '@keyframes lbbstartfade{to{box-shadow:0 0 0 0 transparent}}' +
        '.lbb-start-ping{animation:lbbstartglow 1.6s ease-in-out infinite;border-radius:inherit}' +
        '.lbb-start-ping.lbb-start-fade{animation:lbbstartfade .6s ease-out forwards}';
      doc.head.appendChild(st);
    }
    el.classList.add('lbb-start-ping');
    // Keep glowing until the reader actually engages with the block, then fade.
    const dismiss = () => {
      doc.removeEventListener('pointerdown', dismiss, true);
      doc.removeEventListener('keydown', dismiss, true);
      el.classList.add('lbb-start-fade');
      setTimeout(() => {
        el.classList.remove('lbb-start-ping', 'lbb-start-fade');
        delete el.dataset.lbbPinging;
      }, 650);
    };
    doc.addEventListener('pointerdown', dismiss, true);
    doc.addEventListener('keydown', dismiss, true);
  };

  // Mirror the page's theme into the (same-origin) preview so a block matches the
  // surrounding docs when the reader toggles light/dark.
  const lbbSyncFrameTheme = (frame) => {
    let idoc;
    try { idoc = frame.contentDocument; } catch (_) { return; }
    if (!idoc || !idoc.documentElement) return;
    const theme = document.documentElement.getAttribute('data-theme');
    if (theme) idoc.documentElement.setAttribute('data-theme', theme);
    else idoc.documentElement.removeAttribute('data-theme');
  };

  const io = ('IntersectionObserver' in window)
    ? new IntersectionObserver((entries, obs) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { obs.unobserve(e.target); lbbLoadFrame(e.target); }
        });
      }, { rootMargin: '300px' })
    : null;

  const lbbScanFrames = () => {
    document.querySelectorAll('iframe[data-lbb-src]').forEach((f) => {
      if (!f.dataset.lbbPingWired) {
        f.dataset.lbbPingWired = '1';
        f.addEventListener('load', () => { lbbSyncFrameTheme(f); lbbAddStartPing(f); });
      }
      if (io && f.hasAttribute('data-lbb-lazy')) {
        if (!f.dataset.lbbObserved) { f.dataset.lbbObserved = '1'; io.observe(f); }
      } else {
        // Eager: defer past the current task so hydration/morph has settled
        // (loading during parse gets clobbered by the morph → a blank frame).
        requestAnimationFrame(() => lbbLoadFrame(f));
      }
    });
  };

  const lbbHasPreviewFrame = (node) =>
    node.nodeType === 1 &&
    (node.matches?.('iframe[data-lbb-src]') || node.querySelector?.('iframe[data-lbb-src]'));

  lbbScanFrames();
  document.addEventListener('DOMContentLoaded', lbbScanFrames);
  // React to morphs two ways: a re-added viewer (new/reset frame) → rescan; a
  // switched block reuses the same iframe and only rewrites data-lbb-src → reload
  // that frame directly. Without the attribute path a tab/slide switch keeps the
  // old preview.
  new MutationObserver((muts) => {
    let rescan = false;
    for (const m of muts) {
      if (m.type === 'attributes') { lbbLoadFrame(m.target); continue; }
      for (const n of m.addedNodes) if (lbbHasPreviewFrame(n)) { rescan = true; break; }
    }
    if (rescan) lbbScanFrames();
  }).observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['data-lbb-src'],
  });

  // Propagate a page theme toggle to every loaded preview.
  new MutationObserver(() => {
    document.querySelectorAll('iframe[data-lbb-src]').forEach(lbbSyncFrameTheme);
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
}

function lbbCopy(el, text) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = el.dataset.tip;
    el.dataset.tip = 'Copied!';
    el.querySelector('.i-copy').style.display = 'none';
    el.querySelector('.i-check').style.display = '';
    setTimeout(() => {
      el.dataset.tip = orig;
      el.querySelector('.i-copy').style.display = '';
      el.querySelector('.i-check').style.display = 'none';
    }, 2000);
  });
}

function lbbCopyInstall(el) {
  const cmd = el.closest('[data-install-cmd]')?.dataset.installCmd ?? '';
  lbbCopy(el, cmd);
}

// Split an hljs-highlighted <code> into per-line .src-line spans WITHOUT losing
// the syntax tokens — we re-open any hljs span left open at each line break. This
// gives us line numbers (CSS counter) and a highlightable line range, and unlike
// a textContent rebuild it preserves the colours. Copy still yields plain text.
function lbbWrapLines(code) {
  if (code.dataset.lined) return;
  const html = code.innerHTML;
  const open = [];
  let out = '<span class="src-line">';
  const re = /<[^>]+>|\n|[^<\n]+/g;
  let m;
  while ((m = re.exec(html))) {
    const t = m[0];
    if (t === '\n') {
      out += '</span>'.repeat(open.length) + '</span><span class="src-line">' + open.join('');
    } else if (t[0] === '<') {
      if (t[1] === '/') open.pop();
      else if (t[t.length - 2] !== '/') open.push(t);
      out += t;
    } else {
      out += t;
    }
  }
  code.innerHTML = out + '</span>';
  code.dataset.lined = '1';
}

function lbbCopyCode(el) {
  const panel = el.closest('.lbb-source');
  const tabs = (panel ?? document).querySelectorAll('.src-tab');
  const visible = Array.from(tabs).find(t => t.style.display !== 'none');
  const code = visible?.querySelector('code');
  if (!code) return lbbCopy(el, '');
  const lines = code.querySelectorAll('.src-line');
  lbbCopy(el, lines.length
    ? Array.from(lines).map(l => l.textContent).join('\n')
    : code.textContent);
}

// A guided-tour step: highlight lines [start..end] of the active file in the
// named viewer's source panel and scroll them into view within the code pane.
function lbbTourHighlight(viewerId, file, start, end) {
  setTimeout(() => {
    const root = document.getElementById(viewerId + '-source');
    if (!root) return;
    const tab = root.querySelector('.src-tab[data-file="' + CSS.escape(file) + '"]');
    const code = tab && tab.querySelector('code');
    if (!code) return;
    if (!code.dataset.lined) lbbWrapLines(code);
    root.querySelectorAll('.src-line.tour-hl').forEach(l => l.classList.remove('tour-hl'));
    const lines = code.querySelectorAll('.src-line');
    let first = null;
    for (let i = start; i <= end && i <= lines.length; i++) {
      const ln = lines[i - 1];
      if (!ln) continue;
      ln.classList.add('tour-hl');
      if (!first) first = ln;
    }
    if (first) {
      const box = code.closest('.overflow-auto');
      if (box) {
        const c = box.getBoundingClientRect(), l = first.getBoundingClientRect();
        box.scrollTop += (l.top - c.top) - box.clientHeight / 2 + l.height / 2;
      }
    }
  }, 60);
}

// Line-wrap each code block only AFTER hljs colours it (it stamps
// data-highlighted="yes"). We never call hljs on the initial blocks — its own
// highlightAll() does one pass; re-highlighting a block we already wrapped is
// what collapsed the code (hljs rebuilds from textContent, losing our newlines).
// Morph-added code (e.g. the homepage slider) is fresh, so colouring it is safe.
if (!window.__lbbSourceSetup) {
  window.__lbbSourceSetup = true;
  let loaded = false;

  const wrapReady = (code) => { if (code.dataset.highlighted === 'yes' && !code.dataset.lined) lbbWrapLines(code); };
  const scanReady = () => document.querySelectorAll('.src-tab code[data-highlighted="yes"]:not([data-lined])').forEach(wrapReady);

  // The morph strips our data-* markers with the old content, so an unlined
  // <code> is always new source — never something we'd double-highlight.
  const processCode = (code) => {
    if (!code || code.dataset.lined) return;
    if (window.hljs && !code.dataset.highlighted) {
      try { window.hljs.highlightElement(code); } catch (_) {}
    }
    lbbWrapLines(code);
  };

  scanReady();
  document.addEventListener('DOMContentLoaded', () => setTimeout(scanReady, 0));
  window.addEventListener('load', () => {
    loaded = true;
    scanReady();
    if (!window.hljs) document.querySelectorAll('.src-tab code:not([data-lined])').forEach(lbbWrapLines);
  });

  new MutationObserver((muts) => {
    lbbEnsureSrcStyle(); // a morph may have just dropped it from <head>
    for (const m of muts) {
      if (m.type === 'attributes') {
        if (m.target.nodeName === 'CODE' && m.target.closest('.src-tab')) wrapReady(m.target);
        continue;
      }
      if (!loaded) continue; // ignore initial hydration; hljs handles those
      // Switching block morphs a <code>'s children in place: the added node is a
      // text node and <code> is never re-added, so neither branch below sees it.
      if (m.target.nodeType === 1) processCode(m.target.closest?.('.src-tab code'));
      for (const n of m.addedNodes) {
        if (n.nodeType !== 1) continue;
        const codes = n.matches?.('.src-tab code:not([data-lined])') ? [n]
          : n.querySelectorAll?.('.src-tab code:not([data-lined])');
        codes && codes.forEach(processCode);
      }
    }
  }).observe(document.documentElement, {
    childList: true, subtree: true, attributes: true, attributeFilter: ['data-highlighted'],
  });
}

// Line numbers, tour highlight, and a theme-aware override of hljs's fixed
// GitHub-Dark palette (unreadable on labb-light). Re-checked, not injected
// once: a morph rebuilds <head> and drops this tag.
function lbbEnsureSrcStyle() {
  if (document.getElementById('lbb-src-style')) return;
  const s = document.createElement('style');
  s.id = 'lbb-src-style';
  s.textContent = [
    '.lbb-source pre{white-space:pre}',
    '.lbb-source code{counter-reset:lbbln}',
    '.lbb-source .src-line{display:block;white-space:pre;min-height:1.2em;min-width:100%;counter-increment:lbbln}',
    '.lbb-source .src-line::before{content:counter(lbbln);display:inline-block;width:2.5rem;padding-right:1rem;text-align:right;color:color-mix(in oklab,var(--color-base-content) 28%,transparent);user-select:none;-webkit-user-select:none}',
    '.lbb-source .src-line.tour-hl{background:color-mix(in oklab,var(--color-warning) 18%,transparent);box-shadow:inset 3px 0 0 var(--color-warning)}',
    '.lbb-source .hljs{color:color-mix(in oklab,var(--color-base-content) 92%,transparent)}',
    '.lbb-source .hljs-comment,.lbb-source .hljs-quote{color:color-mix(in oklab,var(--color-base-content) 42%,transparent);font-style:italic}',
    '.lbb-source .hljs-keyword,.lbb-source .hljs-selector-tag,.lbb-source .hljs-built_in,.lbb-source .hljs-name,.lbb-source .hljs-tag,.lbb-source .hljs-literal,.lbb-source .hljs-doctag{color:color-mix(in oklab,var(--color-base-content) 96%,transparent);font-weight:500}',
    '.lbb-source .hljs-string,.lbb-source .hljs-attr,.lbb-source .hljs-attribute,.lbb-source .hljs-symbol,.lbb-source .hljs-meta .hljs-string,.lbb-source .hljs-addition{color:var(--color-info)}',
    '.lbb-source .hljs-number,.lbb-source .hljs-type,.lbb-source .hljs-title,.lbb-source .hljs-title.function_,.lbb-source .hljs-title.class_,.lbb-source .hljs-selector-id,.lbb-source .hljs-selector-class,.lbb-source .hljs-variable,.lbb-source .hljs-template-variable,.lbb-source .hljs-params{color:color-mix(in oklab,var(--color-base-content) 66%,transparent)}',
    '.lbb-source .hljs-meta{color:color-mix(in oklab,var(--color-base-content) 52%,transparent)}',
    '@keyframes lbb-url-flash{0%{background-color:color-mix(in oklab,var(--color-warning) 40%,transparent)}100%{background-color:transparent}}',
    '.lbb-url-flash{animation:lbb-url-flash 1.6s ease-out;border-radius:3px;padding:0 3px;margin:0 -3px}',
  ].join('');
  document.head.appendChild(s);
}

lbbEnsureSrcStyle();
