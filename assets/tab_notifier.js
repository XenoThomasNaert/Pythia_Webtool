(function () {
    var originalFaviconHref = null;
    var badgeActive = false;
    var wasCalculating = false;

    function getFaviconLink() {
        return document.querySelector("link[rel~='icon']");
    }

    function ensureOriginalStored() {
        if (originalFaviconHref) return;
        var link = getFaviconLink();
        if (link) originalFaviconHref = link.href;
    }

    function showBadge() {
        if (badgeActive) return;
        ensureOriginalStored();
        var link = getFaviconLink();
        if (!link || !originalFaviconHref) return;

        var img = new Image();
        img.onload = function () {
            var canvas = document.createElement('canvas');
            canvas.width = 32;
            canvas.height = 32;
            var ctx = canvas.getContext('2d');

            ctx.drawImage(img, 0, 0, 32, 32);

            // Red dot in top-right corner
            ctx.beginPath();
            ctx.arc(26, 6, 6, 0, 2 * Math.PI);
            ctx.fillStyle = '#E53E3E';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();

            link.href = canvas.toDataURL('image/png');
            badgeActive = true;
        };
        img.src = originalFaviconHref;
    }

    function hideBadge() {
        if (!badgeActive) return;
        var link = getFaviconLink();
        if (link && originalFaviconHref) link.href = originalFaviconHref;
        badgeActive = false;
    }

    function onTitleChange() {
        var title = document.title;
        if (title.indexOf('Calculating') !== -1) {
            wasCalculating = true;
        } else if (wasCalculating) {
            wasCalculating = false;
            // Calculation finished — badge only if the user isn't looking at this tab
            if (document.visibilityState === 'hidden' || !document.hasFocus()) {
                showBadge();
            }
        }
    }

    function watchTitle() {
        var titleEl = document.querySelector('title');
        if (!titleEl) return;
        new MutationObserver(onTitleChange).observe(titleEl, {
            childList: true,
            characterData: true,
            subtree: true
        });
    }

    // Remove badge when the user returns to this tab
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') hideBadge();
    });
    window.addEventListener('focus', hideBadge);

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            ensureOriginalStored();
            watchTitle();
        });
    } else {
        ensureOriginalStored();
        watchTitle();
    }
})();
