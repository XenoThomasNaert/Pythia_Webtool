function updateTaggingOffset() {
    const headerTop = document.querySelector(".header-top-row");
    const headerNav = document.querySelector(".header-nav");

    const h1 = headerTop ? headerTop.offsetHeight : 0;
    const h2 = headerNav ? headerNav.offsetHeight : 0;
    const total = h1 + h2;

    document.documentElement.style.setProperty(
        "--tagging-bar-offset",
        total + "px"
    );
}

function setupStickyAnimation() {
    const stickyEl = document.querySelector(".tagging-bar-sticky");
    if (!stickyEl) return;

    // Remove old observer if it exists
    if (stickyEl._observer) {
        stickyEl._observer.disconnect();
    }

    const observer = new IntersectionObserver(
        ([entry]) => {
            if (entry.intersectionRatio < 1) {
                stickyEl.classList.add("is-sticky");
            } else {
                stickyEl.classList.remove("is-sticky");
            }
        },
        { threshold: [1] }
    );

    observer.observe(stickyEl);
    stickyEl._observer = observer;
}

function setupMutationObserver() {
    const targetNode = document.getElementById("mutation-detail-container");
    if (!targetNode) return;
    
    // Don't create duplicate observers
    if (targetNode._contentObserver) return;
    
    const observer = new MutationObserver(() => {
        setTimeout(() => {
            updateTaggingOffset();
            setupStickyAnimation();
        }, 50);
    });
    
    observer.observe(targetNode, {
        childList: true,
        subtree: true
    });
    
    targetNode._contentObserver = observer;
}

// Run on load
window.addEventListener("load", () => {
    updateTaggingOffset();
    setupStickyAnimation();
    setupMutationObserver();
});

// Run when window resizes
window.addEventListener("resize", updateTaggingOffset);

// 🔥 THE CRITICAL FIX 🔥
// Set up observer when container appears (for initial load)
const bodyObserver = new MutationObserver(() => {
    setupMutationObserver();
});

bodyObserver.observe(document.body, {
    childList: true,
    subtree: true
});

// Remove animation classes after first render to enable smooth transitions
document.addEventListener('DOMContentLoaded', function() {
    // Use MutationObserver to detect when new elements are added to the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // Find all elements with animation classes
                    const animatedElements = node.querySelectorAll 
                        ? node.querySelectorAll('.tagging-insert-appear, .tagging-blue-left, .tagging-blue-right-extra, .tagging-grey-appear')
                        : [];
                    
                    // Also check if the node itself has the class
                    if (node.classList && (
                        node.classList.contains('tagging-insert-appear') ||
                        node.classList.contains('tagging-blue-left') ||
                        node.classList.contains('tagging-blue-right-extra') ||
                        node.classList.contains('tagging-grey-appear')
                    )) {
                        removeAnimationAfterDelay(node);
                    }
                    
                    // Remove animation class from children after animation completes
                    animatedElements.forEach(function(element) {
                        removeAnimationAfterDelay(element);
                    });
                }
            });
        });
    });
    
    function removeAnimationAfterDelay(element) {
        // Wait for animation to complete (450ms + 100ms delay)
        setTimeout(function() {
            // Store the current computed values
            const computedStyle = getComputedStyle(element);
            const currentWidth = computedStyle.width;
            const currentLeft = computedStyle.left;
            
            // Replace animation class with transition class
            if (element.classList.contains('tagging-insert-appear')) {
                element.classList.remove('tagging-insert-appear');
                element.classList.add('tagging-insert-transition');
                // Set inline styles to preserve state
                element.style.width = currentWidth;
                element.style.left = currentLeft;
            }
            if (element.classList.contains('tagging-blue-left')) {
                element.classList.remove('tagging-blue-left');
                element.classList.add('tagging-blue-transition');
                element.style.width = currentWidth;
                element.style.left = currentLeft;
            }
            if (element.classList.contains('tagging-blue-right-extra')) {
                element.classList.remove('tagging-blue-right-extra');
                element.classList.add('tagging-blue-transition');
                element.style.width = currentWidth;
                element.style.left = currentLeft;
            }
            if (element.classList.contains('tagging-grey-appear')) {
                element.classList.remove('tagging-grey-appear');
                element.classList.add('tagging-grey-transition');
                element.style.width = currentWidth;
                element.style.left = currentLeft;
            }
            
            // Now observe for style attribute changes to sync with Python updates
            setupStyleSync(element);
        }, 600); // 450ms animation + 100ms delay + 50ms buffer
    }
    
    function setupStyleSync(element) {
        if (element._styleObserver) return; // Don't create duplicates
        
        const styleObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    // Python has updated the style, sync it to inline styles
                    const computedStyle = getComputedStyle(element);
                    
                    // Check if CSS variables have changed
                    const finalWidth = computedStyle.getPropertyValue('--final-width').trim();
                    const finalLeft = computedStyle.getPropertyValue('--final-left').trim();
                    
                    if (finalWidth && finalWidth !== element.style.width) {
                        element.style.width = finalWidth;
                    }
                    if (finalLeft && finalLeft !== element.style.left) {
                        element.style.left = finalLeft;
                    }
                }
            });
        });
        
        styleObserver.observe(element, {
            attributes: true,
            attributeFilter: ['style']
        });
        
        element._styleObserver = styleObserver;
    }
    
    // Observe the entire document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
