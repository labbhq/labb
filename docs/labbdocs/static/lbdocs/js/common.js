// Common JavaScript functionality for Labb documentation

document.addEventListener('DOMContentLoaded', function () {
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }

    scrollToActiveMenuItem();
    initTocScrollspy();
    initBannerDismiss();
});

/**
 * Scroll to the active menu item in the docs sidebar
 */
function scrollToActiveMenuItem() {
    const sidebarMenu = document.getElementById('docs-sidebar-menu');
    if (!sidebarMenu) return;

    // Find the active menu item
    const activeMenuItem = sidebarMenu.querySelector('.active');
    if (!activeMenuItem) return;

    // Find the scrollable container using the docs-sidebar-container class
    const scrollContainer = sidebarMenu.closest('.docs-sidebar-container');
    if (!scrollContainer) return;

    // Calculate the scroll position to center the active item
    const containerRect = scrollContainer.getBoundingClientRect();
    const itemRect = activeMenuItem.getBoundingClientRect();
    const containerTop = containerRect.top;
    const itemTop = itemRect.top;
    const itemHeight = itemRect.height;
    const containerHeight = containerRect.height;

    // Calculate the scroll offset to center the item
    const scrollOffset = itemTop - containerTop - (containerHeight / 2) + (itemHeight / 2);

    // Scroll the container directly with smooth behavior
    setTimeout(() => {
        scrollContainer.scrollTo({
            top: scrollContainer.scrollTop + scrollOffset,
            behavior: 'smooth'
        });
    }, 100);
}


/**
 * Highlight the TOC entry for the heading currently in view.
 */
function initTocScrollspy() {
    const toc = document.getElementById('toc-sidebar');
    const article = document.querySelector('article');
    if (!toc || !article) return;

    const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
    if (!links.length) return;

    const linkById = new Map();
    links.forEach(function (link) {
        const id = decodeURIComponent(link.getAttribute('href').slice(1));
        if (id) linkById.set(id, link);
    });

    const headings = Array.from(article.querySelectorAll('h2, h3, h4'))
        .filter(function (h) { return h.id && linkById.has(h.id); });
    if (!headings.length) return;

    let activeId = null;
    function setActive(id) {
        if (id === activeId || !linkById.has(id)) return;
        activeId = id;
        links.forEach(function (link) { link.classList.remove('menu-active'); });
        linkById.get(id).classList.add('menu-active');
    }

    const visible = new Set();
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) visible.add(entry.target);
            else visible.delete(entry.target);
        });
        if (visible.size) {
            // When several headings are visible, the topmost one wins.
            const top = Array.from(visible).sort(function (a, b) {
                return a.getBoundingClientRect().top - b.getBoundingClientRect().top;
            })[0];
            setActive(top.id);
        }
    }, { rootMargin: '0px 0px -70% 0px', threshold: 0 });

    headings.forEach(function (h) { observer.observe(h); });

    // Clamp the edges: first heading active at the top, last at the bottom.
    function clampEdges() {
        if (window.scrollY <= 8) {
            setActive(headings[0].id);
            return;
        }
        const bottom = window.innerHeight + window.scrollY;
        if (bottom >= document.documentElement.scrollHeight - 8) {
            setActive(headings[headings.length - 1].id);
        }
    }
    window.addEventListener('scroll', clampEdges, { passive: true });

    setActive(headings[0].id);
    clampEdges();
}

/**
 * Dismiss the announcement banner and persist it server-side.
 *
 * Persisting matters: a Datastar full-page morph would otherwise re-emit the
 * banner. Config comes from data attributes so this file stays static.
 */
function initBannerDismiss() {
    const button = document.querySelector('[data-banner-dismiss]');
    if (!button) return;

    button.addEventListener('click', function () {
        const id = button.dataset.bannerDismiss;
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';

        // Drop the header-height offset immediately so content reflows
        // without waiting for a full-page morph.
        document.documentElement.classList.remove('lb-has-banner');

        fetch(button.dataset.dismissUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': button.dataset.csrfToken,
            },
            body: 'banner_id=' + encodeURIComponent(id),
        }).catch(function () {});
    });
}


function copyToClipboard(text, elementId) {
    navigator.clipboard.writeText(text);
    document.getElementById(`${elementId}-copied`).classList.remove('hidden');
    setTimeout(() => {
        document.getElementById(`${elementId}-copied`).classList.add('hidden');
    }, 1000);
}

/**
 * Copy code block content to clipboard
 * @param {HTMLElement} button - The copy button element that was clicked
 */
function copyCodeBlock(button) {
    const container = button.closest('.codeblock-container');
    if (!container) return;

    const codeElement = container.querySelector('.code-content');
    if (!codeElement) return;

    const text = codeElement.textContent || codeElement.innerText;

    navigator.clipboard.writeText(text).then(() => {
        const copiedNotification = container.querySelector('.copy-notification');
        if (copiedNotification) {
            copiedNotification.classList.remove('hidden');
            setTimeout(() => {
                copiedNotification.classList.add('hidden');
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy code:', err);
    });
}
