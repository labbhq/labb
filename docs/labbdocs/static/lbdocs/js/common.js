// Common JavaScript functionality for Labb documentation

// Initialize common functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function () {

    // Initialize syntax highlighting
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }

    // Scroll to active menu item in docs sidebar
    scrollToActiveMenuItem();

    // Setup toggle behavior for submenu-details (collapse when clicking outside)
    setupSubmenuDetailsToggle();
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

/**
 * Collapse submenu-details when clicking outside of them
 * Only collapses details where the parent <li> has the 'auto-collapse' class
 * This provides toggle behavior - clicking outside closes open details
 */
function setupSubmenuDetailsToggle() {
    // Add click event listener to the document
    document.addEventListener('click', function(event) {
        // Find all open details elements where parent <li> has 'auto-collapse' class
        const allDetails = document.querySelectorAll('li details[open]');
        const autoCollapseDetails = Array.from(allDetails).filter(details => {
            const parentLi = details.closest('li');
            return parentLi && parentLi.classList.contains('auto-collapse');
        });

        if (autoCollapseDetails.length === 0) return;

        // Check if the click was inside any of these details elements
        let clickedInsideDetails = false;
        autoCollapseDetails.forEach(details => {
            if (details.contains(event.target)) {
                clickedInsideDetails = true;
            }
        });

        // If click was outside all auto-collapse details elements, close them
        if (!clickedInsideDetails) {
            autoCollapseDetails.forEach(details => {
                details.removeAttribute('open');
            });
        }
    });
}
