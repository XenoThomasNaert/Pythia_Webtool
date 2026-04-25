(function () {

    function showPythiaTimeoutError() {
        var existing = document.getElementById('pythia-timeout-notification');
        if (existing) existing.remove();

        var notification = document.createElement('div');
        notification.id = 'pythia-timeout-notification';
        notification.style.cssText = [
            'position:fixed',
            'top:80px',
            'right:20px',
            'z-index:99999',
            'background:#FFF8E1',
            'border:2px solid #F59E0B',
            'border-radius:10px',
            'padding:18px 22px',
            'max-width:480px',
            'box-shadow:0 6px 16px rgba(0,0,0,0.15)',
            'font-family:Helvetica,Arial,sans-serif',
            'font-size:14px',
            'line-height:1.6'
        ].join(';');

        notification.innerHTML = [
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;">',
            '  <strong style="font-size:16px;color:#92400E;">&#9888; Request timed out</strong>',
            '  <button',
            '    onclick="document.getElementById(\'pythia-timeout-notification\').remove()"',
            '    style="background:none;border:none;font-size:20px;cursor:pointer;color:#92400E;margin-left:12px;padding:0;line-height:1;"',
            '  >&#10005;</button>',
            '</div>',
            '<p style="margin:10px 0 6px;color:#78350F;">',
            '  The request was throttled due to server limitations (504 gateway timeout).',
            '  This happens when the analysis takes longer than the hosting server allows.',
            '</p>',
            '<p style="margin:6px 0 0;color:#78350F;">',
            '  To avoid this limitation, run Pythia locally using <strong>Docker</strong>',
            '  or by cloning the repository from <strong>GitHub</strong> &mdash;',
            '  local runs have no time restrictions.',
            '</p>'
        ].join('');

        document.body.appendChild(notification);

        setTimeout(function () {
            var n = document.getElementById('pythia-timeout-notification');
            if (n) n.remove();
        }, 20000);
    }

    // Expose globally so the test button clientside_callback can call it
    window.showPythiaTimeoutError = showPythiaTimeoutError;

    // Intercept console.error to detect Dash callback errors.
    // When a 504 occurs, Dash logs: { message: "Callback error ...", html: "<html>...504..." }
    var originalConsoleError = console.error;
    console.error = function () {
        try {
            var first = arguments[0];
            if (first && typeof first === 'object' && typeof first.html === 'string') {
                var h = first.html;
                if (
                    h.indexOf('504') !== -1 ||
                    h.indexOf('loadbalancer') !== -1 ||
                    h.indexOf('Something went wrong') !== -1
                ) {
                    showPythiaTimeoutError();
                }
            }
        } catch (e) { /* never block the original call */ }
        return originalConsoleError.apply(console, arguments);
    };

})();
