import dash_bootstrap_components as dbc
from dash import dcc, html


INDEX_STRING = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" type="image/png" href="/assets/favicon.png">
        {%css%}
        <style>
            :root {
                /* Modern Scientific Color Palette */
                --primary-color: #2E5BFF;        /* Deep blue for trust and science */
                --primary-hover: #1D4ED8;        /* Darker blue for hover states */
                --secondary-color: #10B981;      /* Emerald green for biotechnology */
                --secondary-hover: #059669;      /* Darker green for hover states */
                --accent-color: #F59E0B;         /* Orange for highlights and CTAs */
                --accent-hover: #D97706;         /* Darker orange for hover states */

                /* Neutral Colors */
                --background-primary: #FFFFFF;   /* Clean white */
                --background-secondary: #F9FAFB; /* Light gray background */
                --background-tertiary: #F3F4F6;  /* Slightly darker gray */

                /* Text Colors */
                --text-primary: #111827;         /* Dark gray for primary text */
                --text-secondary: #6B7280;       /* Medium gray for secondary text */
                --text-muted: #9CA3AF;           /* Light gray for muted text */

                /* Border and Shadow */
                --border-color: #E5E7EB;         /* Light border */
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

                /* Semantic Colors */
                --success-color: #10B981;        /* Green for success states */
                --warning-color: #F59E0B;        /* Orange for warnings */
                --error-color: #EF4444;          /* Red for errors */
                --info-color: #3B82F6;           /* Blue for info */

                /* Typography */
                --font-family-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                --font-family-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;

                /* Font Sizes */
                --font-size-xs: 0.75rem;    /* 12px */
                --font-size-sm: 0.875rem;   /* 14px */
                --font-size-base: 1rem;     /* 16px */
                --font-size-lg: 1.125rem;   /* 18px */
                --font-size-xl: 1.25rem;    /* 20px */
                --font-size-2xl: 1.5rem;    /* 24px */
                --font-size-3xl: 1.875rem;  /* 30px */
                --font-size-4xl: 2.25rem;   /* 36px */
                --font-size-5xl: 3rem;      /* 48px */

                /* Border Radius */
                --border-radius-sm: 0.25rem;   /* 4px */
                --border-radius: 0.375rem;     /* 6px */
                --border-radius-md: 0.5rem;    /* 8px */
                --border-radius-lg: 0.75rem;   /* 12px */
                --border-radius-xl: 1rem;      /* 16px */

                /* Spacing Scale */
                --spacing-xs: 0.25rem;    /* 4px */
                --spacing-sm: 0.5rem;     /* 8px */
                --spacing-md: 0.75rem;    /* 12px */
                --spacing-lg: 1rem;       /* 16px */
                --spacing-xl: 1.5rem;     /* 24px */
                --spacing-2xl: 2rem;      /* 32px */
                --spacing-3xl: 3rem;      /* 48px */
                --spacing-4xl: 4rem;      /* 64px */
            }

            /* Apply modern typography to body and common elements */
            body {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-base);
                color: var(--text-primary);
                line-height: 1.6;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }

            /* Heading hierarchy */
            h1 {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-4xl);
                color: var(--text-primary);
                font-weight: 700;
                line-height: 1.2;
                margin-bottom: 1rem;
            }

            h2 {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-3xl);
                color: var(--text-primary);
                font-weight: 600;
                line-height: 1.3;
                margin-bottom: 0.875rem;
            }

            h3 {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-2xl);
                color: var(--text-primary);
                font-weight: 600;
                line-height: 1.3;
                margin-bottom: 0.75rem;
            }

            h4 {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-xl);
                color: var(--text-primary);
                font-weight: 600;
                line-height: 1.4;
                margin-bottom: 0.625rem;
            }

            h5, h6 {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-lg);
                color: var(--text-primary);
                font-weight: 600;
                line-height: 1.4;
                margin-bottom: 0.5rem;
            }

            p {
                font-family: var(--font-family-primary);
                font-size: var(--font-size-base);
                color: var(--text-secondary);
                line-height: 1.6;
                margin-bottom: 1rem;
            }

            /* Gene visualization smooth transitions */
            #mutation-detail-container > div > div > div > div {
                transition: width 0.5s ease-in-out, left 0.5s ease-in-out, max-width 0.5s ease-in-out !important;
            }

            /* Fade in animation for new content */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            #mutation-detail-container {
                animation: fadeIn 0.3s ease-in-out;
            }

            /* Small text utility */
            .text-sm {
                font-size: var(--font-size-sm);
            }

            .text-xs {
                font-size: var(--font-size-xs);
            }

            /* Modern Button Styling */
            button,
            .btn,
            input[type="submit"],
            input[type="button"] {
                border-radius: var(--border-radius-md) !important;
                font-family: var(--font-family-primary) !important;
                font-weight: 500 !important;
                transition: all 0.2s ease-in-out !important;
                border: 1px solid transparent !important;
                cursor: pointer !important;
            }

            /* Primary button styling (Bootstrap btn-primary override) */
            .btn-primary {
                background-color: var(--primary-color) !important;
                border-color: var(--primary-color) !important;
                color: white !important;
            }

            .btn-primary:hover {
                background-color: var(--primary-hover) !important;
                border-color: var(--primary-hover) !important;
                transform: translateY(-1px) !important;
                box-shadow: var(--shadow-md) !important;
            }

            /* Secondary button styling */
            .btn-secondary {
                background-color: var(--background-tertiary) !important;
                border-color: var(--border-color) !important;
                color: var(--text-primary) !important;
            }

            .btn-secondary:hover {
                background-color: var(--background-secondary) !important;
                transform: translateY(-1px) !important;
                box-shadow: var(--shadow-sm) !important;
            }

            /* Generic button styling for non-Bootstrap buttons */
            button:not(.btn) {
                background-color: var(--primary-color);
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                font-size: var(--font-size-sm);
            }

            button:not(.btn):hover {
                background-color: var(--primary-hover);
                transform: translateY(-1px);
                box-shadow: var(--shadow-md);
            }

            /* Subtle Box Shadows for Depth */

            /* Main content containers */
            #page-content > div {
                box-shadow: var(--shadow-sm);
            }

            /* Form containers and input groups */
            .form-group,
            div[style*="display: flex"]:has(input),
            div[style*="display: flex"]:has(.dropdown) {
                background-color: var(--background-primary);
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-sm);
                transition: box-shadow 0.2s ease-in-out;
            }

            /* Enhanced shadows on hover for interactive containers */
            .form-group:hover,
            div[style*="display: flex"]:has(input):hover {
                box-shadow: var(--shadow-md);
            }

            /* Data tables and result containers */
            .dash-table-container,
            #table-container,
            #table-container2,
            #table-container3 {
                background-color: var(--background-primary);
                border-radius: var(--border-radius-lg);
                box-shadow: var(--shadow-md);
                padding: 1rem;
                margin: 1rem 0;
            }

            /* Loading components */
            .dash-loading {
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-sm);
            }

            /* Input fields */
            input,
            select,
            textarea,
            .Select-control {
                box-shadow: var(--shadow-sm) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: var(--border-radius) !important;
                transition: all 0.2s ease-in-out !important;
            }

            input:focus,
            select:focus,
            textarea:focus,
            .Select-control:focus {
                box-shadow: 0 0 0 3px rgba(46, 91, 255, 0.1), var(--shadow-md) !important;
                border-color: var(--primary-color) !important;
                outline: none !important;
            }

            /* Dropdown menus */
            .Select-menu-outer {
                box-shadow: var(--shadow-lg) !important;
                border-radius: var(--border-radius) !important;
                border: 1px solid var(--border-color) !important;
            }

            /* Refined Spacing and Layout */

            /* Main container spacing */
            #page-content {
                padding: var(--spacing-xl) var(--spacing-lg);
                max-width: 1400px;
                margin: 0 auto;
            }

            /* Section spacing */
            div[style*="margin"]:not([style*="marginBottom: '2em'"]):not(.allele-panel):not(.allele-panel *):not(.grna-title-row):not(.grna-title-row *) {
                margin-bottom: 0 !important;
            }

            /* Form element spacing */
            input, select, textarea {
                padding: var(--spacing-md) var(--spacing-lg) !important;
                margin-bottom: var(--spacing-md) !important;
            }

            /* Button spacing and sizing */
            button, .btn {
                padding: var(--spacing-md) var(--spacing-xl) !important;
                margin: var(--spacing-sm) var(--spacing-xs) !important;
            }

            /* Improved paragraph spacing */
            p {
                margin-bottom: var(--spacing-lg);
                margin-top: var(--spacing-sm);
            }

            /* Section dividers */
            div[style*="backgroundColor: grey"] {
                margin: var(--spacing-2xl) 0 !important;
                background-color: var(--border-color) !important;
                height: 1px !important;
                box-shadow: none !important;
            }

            /* Logo and image spacing */
            img {
                margin: var(--spacing-sm) var(--spacing-xs);
            }

            /* Form group spacing */
            .form-group {
                margin-bottom: var(--spacing-xl);
                padding: var(--spacing-lg);
            }

            /* Input container spacing */
            div[style*="display: flex"] {
                gap: var(--spacing-md);
                margin-bottom: var(--spacing-lg);
            }

            /* Example buttons container */
            div:has(> button[id*="autofill"]) {
                padding: var(--spacing-lg);
                margin: var(--spacing-lg) 0;
                gap: var(--spacing-sm);
            }

            /* Loading component spacing — no extra space; content handles its own layout */
            .dash-loading {
                margin: 0;
                padding: 0;
            }

            /* Dropdown spacing */
            .dropdown {
                margin-bottom: var(--spacing-lg);
            }

            /* Table container improvements */
            .dash-table-container {
                margin: var(--spacing-2xl) 0;
                padding: var(--spacing-xl);
            }

            /* Responsive spacing adjustments */
            @media (max-width: 768px) {
                #page-content {
                    padding: var(--spacing-lg) var(--spacing-md);
                }

                .form-group {
                    padding: var(--spacing-md);
                    margin-bottom: var(--spacing-lg);
                }

                div[style*="display: flex"] {
                    gap: var(--spacing-sm);
                }
            }

            /* Modern Background Color Updates */

            /* Main app background */
            body {
                background-color: var(--background-secondary) !important;
            }

            /* Main content areas */
            #page-content > div {
                background-color: var(--background-primary) !important;
                border-radius: var(--border-radius-lg);
            }

            /* Override inline white backgrounds */
            div[style*="backgroundColor: white"],
            div[style*="backgroundColor: 'white'"] {
                background-color: var(--background-primary) !important;
            }

            /* Form sections and containers */
            .form-section,
            div[style*="padding: 10px"] {
                background-color: var(--background-secondary);
                border-radius: var(--border-radius);
                border: 1px solid var(--border-color);
            }

            /* Input containers with subtle background */
            div[style*="display: flex"]:has(input) {
                background-color: var(--background-secondary);
                padding: var(--spacing-lg);
                border-radius: var(--border-radius-md);
                border: 1px solid var(--border-color);
            }

            /* Loading components */
            .dash-loading {
                background-color: var(--background-primary);
                border: 1px solid var(--border-color);
            }

            /* Table containers */
            .dash-table-container,
            #table-container,
            #table-container2,
            #table-container3 {
                background-color: var(--background-primary) !important;
                border: 1px solid var(--border-color);
            }

            /* Heatmap containers */
            #heatmap1-container,
            #heatmap-editing-output {
                background-color: var(--background-primary) !important;
                border: 1px solid var(--border-color);
            }

            /* Header sections - but NOT for persistent header logos */
            div:not(.persistent-header *):has(> img[src*="Logo"]) {
                background-color: var(--background-primary);
                padding: var(--spacing-lg);
                border-radius: var(--border-radius-md);
                margin-bottom: var(--spacing-xl);
                border: 1px solid var(--border-color);
            }

            /* Disclaimer sections */
            p[style*="fontSize: '0.8em'"] {
                background-color: var(--background-tertiary) !important;
                padding: var(--spacing-lg) !important;
                border-radius: var(--border-radius) !important;
                border: 1px solid var(--border-color) !important;
                color: var(--text-muted) !important;
            }

            /* Two-column layout backgrounds */
            div[style*="flex: '1'"] {
                background-color: var(--background-secondary);
                border-radius: var(--border-radius);
                padding: var(--spacing-lg);
                margin: var(--spacing-sm);
                border: 1px solid var(--border-color);
            }

            /* Inline loading spinner */
            .inline-spinner {
                display: inline-block;
                width: 28px;
                height: 28px;
                border: 3px solid var(--border-color, #E5E7EB);
                border-top-color: var(--primary-color, #2E5BFF);
                border-radius: 50%;
                animation: inline-spin 0.8s linear infinite;
            }

            @keyframes inline-spin {
                to { transform: rotate(360deg); }
            }

            /* Enhanced Card-Style Containers */

            /* Main page content cards */
            #page-content > div {
                background-color: var(--background-primary) !important;
                border-radius: var(--border-radius-xl) !important;
                box-shadow: var(--shadow-lg) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-2xl) !important;
                margin: var(--spacing-xl) auto !important;
                transition: box-shadow 0.3s ease-in-out !important;
            }

            /* Enhanced container hover effects */
            #page-content > div:hover {
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
            }

            /* Form section cards */
            div[style*="flex: '1'"],
            div[style*="padding: '10px'"] {
                background-color: var(--background-primary) !important;
                border-radius: var(--border-radius-lg) !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-xl) !important;
                margin: var(--spacing-md) !important;
                transition: all 0.2s ease-in-out !important;
            }

            /* Form section hover effects */
            div[style*="flex: '1'"]:hover {
                box-shadow: var(--shadow-lg) !important;
                transform: translateY(-2px) !important;
            }

            /* Input group containers */
            div[style*="display: flex"]:has(input),
            div[style*="display: flex"]:has(select) {
                background-color: var(--background-secondary) !important;
                border-radius: var(--border-radius-md) !important;
                box-shadow: var(--shadow-sm) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-lg) !important;
                margin: var(--spacing-md) 0 !important;
                transition: all 0.2s ease-in-out !important;
            }

            /* Input group focus effects */
            div[style*="display: flex"]:has(input:focus),
            div[style*="display: flex"]:has(select:focus) {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(46, 91, 255, 0.1), var(--shadow-md) !important;
                background-color: var(--background-primary) !important;
            }

            /* Override old header logo container - NO BACKGROUNDS for funding logos only */
            .funding-logos,
            .persistent-header div:has(> img[src*="images.png"]),
            .persistent-header div:has(> img[src*="ERC.png"]),
            .persistent-header div:has(> img[src*="swiss.png"]),
            .persistent-header div:has(> img[src*="fwo.png"]),
            .persistent-header div:has(> img[src*="logo_UGent_EN_RGB_2400_color.png"]),
            .persistent-header div:has(> img[src*="uzh.png"]) {
                background: none !important;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                border-radius: 0 !important;
            }

            /* Removed redundant rule - handled by nuclear override below */

            /* Keep old styles only for non-header logo containers */
            div:not(.header-logo):not(.funding-logos):not(.persistent-header *):has(> img[src*="Pythia.png"]) {
                background-color: var(--background-primary) !important;
                border-radius: var(--border-radius-lg) !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-xl) var(--spacing-2xl) !important;
                margin-bottom: var(--spacing-2xl) !important;
            }

            /* Keep old styles only for non-header institution logo containers */
            div:not(.header-logo):not(.funding-logos):not(.persistent-header *):has(> img[src*="images.png"]) {
                background-color: var(--background-secondary) !important;
                border-radius: var(--border-radius-lg) !important;
                box-shadow: var(--shadow-sm) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-xl) !important;
                margin: var(--spacing-xl) 0 !important;
            }

            /* Example buttons container */
            div:has(> button[id*="autofill"]),
            div:has(> button[id*="example"]),
            div:has(> button[id*="guide"]) {
                background-color: var(--background-tertiary) !important;
                border-radius: var(--border-radius-md) !important;
                box-shadow: var(--shadow-sm) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-lg) !important;
                margin: var(--spacing-md) 0 !important;
            }

            /* Result containers enhancement — only when results are present */
            #heatmap1-container:has(.unified-results-container),
            #heatmap-editing-output:has(.unified-results-container),
            #table-container,
            #table-container2,
            #table-container3 {
                background-color: var(--background-primary) !important;
                border-radius: var(--border-radius-xl) !important;
                box-shadow: var(--shadow-lg) !important;
                border: 1px solid var(--border-color) !important;
                padding: var(--spacing-2xl) !important;
                margin: var(--spacing-2xl) 0 !important;
                position: relative !important;
                overflow: hidden !important;
            }

            /* Add subtle gradient to result containers */
            #heatmap1-container:has(.unified-results-container)::before,
            #heatmap-editing-output:has(.unified-results-container)::before,
            #table-container::before,
            #table-container2::before,
            #table-container3::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
                border-radius: var(--border-radius-xl) var(--border-radius-xl) 0 0;
            }

            /* Loading state cards — no extra space; spinner uses native size */
            .dash-loading {
                background-color: var(--background-primary) !important;
                border-radius: var(--border-radius-lg) !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Navigation breadcrumb styling */
            a[href="/"] {
                display: inline-block !important;
                background-color: var(--background-secondary) !important;
                color: var(--primary-color) !important;
                padding: var(--spacing-sm) var(--spacing-lg) !important;
                border-radius: var(--border-radius) !important;
                box-shadow: var(--shadow-sm) !important;
                border: 1px solid var(--border-color) !important;
                text-decoration: none !important;
                font-weight: 500 !important;
                transition: all 0.2s ease-in-out !important;
            }

            a[href="/"]:hover {
                background-color: var(--primary-color) !important;
                color: white !important;
                box-shadow: var(--shadow-md) !important;
                transform: translateY(-1px) !important;
            }

            /* Enhanced Logo and Branding */

            /* Main Pythia logo styling */
            img[src*="Pythia.png"] {
                filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1)) !important;
                transition: all 0.3s ease-in-out !important;
                border-radius: var(--border-radius-sm) !important;
            }

            /* Logo hover effects - REMOVED for static logos */

            /* Home page logo - larger and more prominent */
            .index-page img[src*="Pythia.png"] {
                width: 20% !important;
                max-width: 300px !important;
                min-width: 200px !important;
                height: auto !important;
                margin-bottom: var(--spacing-2xl) !important;
            }

            /* Page 1 and 2 logos - header size */
            div[style*="flex: '1'"] img[src*="Pythia.png"] {
                width: auto !important;
                height: 80px !important;
                max-height: 80px !important;
                margin: var(--spacing-md) !important;
            }

            /* Page 2 centered logo */
            div[style*="margin: auto"] img[src*="Pythia.png"] {
                width: 12% !important;
                max-width: 120px !important;
                min-width: 80px !important;
                height: auto !important;
                margin: var(--spacing-lg) auto !important;
            }

            /* Institution logos enhancement */
            img[src*="images.png"],
            img[src*="ERC.png"],
            img[src*="swiss.png"],
            img[src*="uzh.png"] {
                filter: grayscale(10%) opacity(85%) !important;
                transition: all 0.3s ease-in-out !important;
                border-radius: var(--border-radius-sm) !important;
                margin: var(--spacing-sm) var(--spacing-md) !important;
            }

            /* Persistent Header Navigation Styles */

            /* Main header container - slimmer, full width */
            .persistent-header {
                position: sticky !important;
                top: 0 !important;
                z-index: 9999 !important;
                background-color: var(--background-primary) !important;
                border-bottom: 1px solid var(--border-color) !important;
                box-shadow: var(--shadow-sm) !important;
                padding: var(--spacing-sm) 0 !important;
                margin-bottom: var(--spacing-lg) !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Header layout grid - two rows, slimmer, full width */
            .header-grid {
                display: grid !important;
                grid-template-columns: 1fr auto !important;
                grid-template-rows: auto auto !important;
                gap: var(--spacing-sm) var(--spacing-lg) !important;
                width: 100% !important;
                margin: 0 !important;
                padding: 0 var(--spacing-lg) !important;
                box-sizing: border-box !important;
            }

            /* Header logo styling - clean and minimal */
            .header-logo {
                opacity: 1 !important;
            }

            .header-logo img {
                height: 45px !important;
                width: auto !important;
                filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1)) !important;
            }

            /* Top row - logos, slimmer */
            .header-top-row {
                grid-column: 1 / -1 !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                padding-bottom: var(--spacing-sm) !important;
                border-bottom: 1px solid var(--border-color) !important;
            }

            /* Navigation menu - bottom row, slimmer */
            .header-nav {
                grid-column: 1 / -1 !important;
                display: flex !important;
                gap: var(--spacing-lg) !important;
                align-items: center !important;
                justify-content: center !important;
                padding-top: var(--spacing-sm) !important;
                position: relative !important;
                z-index: 100 !important;
                pointer-events: auto !important;
            }

            .header-nav a {
                color: var(--text-primary) !important;
                text-decoration: none !important;
                font-weight: 500 !important;
                font-size: var(--font-size-base) !important;
                padding: var(--spacing-sm) var(--spacing-lg) !important;
                border-radius: var(--border-radius) !important;
                transition: all 0.2s ease-in-out !important;
                border: 1px solid transparent !important;
                position: relative !important;
                z-index: 10 !important;
                pointer-events: auto !important;
                cursor: pointer !important;
            }

            .header-nav a:hover {
                background-color: var(--background-secondary) !important;
                color: var(--primary-color) !important;
                border-color: var(--border-color) !important;
                transform: translateY(-1px) !important;
            }

            .header-nav a.active {
                background-color: var(--primary-color) !important;
                color: white !important;
                box-shadow: var(--shadow-sm) !important;
            }

            /* Funding logos container - NO background, no boxes */
            .funding-logos {
                background: none !important;
                padding: 0 !important;
                border: none !important;
                box-shadow: none !important;
                border-radius: 0 !important;
                display: flex !important;
                align-items: center !important;
                gap: var(--spacing-sm) !important;
                opacity: 1 !important;
            }

            /* Smaller, compact funding logo sizing */
            .funding-logos img[src*="images.png"] {
                width: 28px !important;
                max-width: 28px !important;
                height: auto !important;
                filter: none !important;
                opacity: 1 !important;
            }

            .funding-logos img[src*="ERC.png"] {
                width: 55px !important;
                max-width: 55px !important;
                height: auto !important;
                filter: none !important;
                opacity: 1 !important;
            }

            .funding-logos img[src*="swiss.png"] {
                width: 60px !important;
                max-width: 60px !important;
                height: auto !important;
                filter: none !important;
                opacity: 1 !important;
            }

            .funding-logos img[src*="fwo.png"] {
                width: 30px !important;
                max-width: 30px !important;
                height: auto !important;
                filter: none !important;
                opacity: 1 !important;
            }

            .funding-logos img[src*="logo_UGent_EN_RGB_2400_color.png"] {
                width: 45px !important;
                max-width: 45px !important;
                height: auto !important;
                filter: none !important;
                opacity: 1 !important;
            }

            .funding-logos img[src*="uzh.png"] {
                width: 50px !important;
                max-width: 50px !important;
                height: auto !important;
                filter: none !important;
                opacity: 1 !important;
            }

            /* Mobile header responsiveness */
            @media (max-width: 768px) {
                .header-grid {
                    grid-template-columns: 1fr !important;
                    gap: var(--spacing-sm) !important;
                }

                .header-top-row {
                    flex-direction: column !important;
                    gap: var(--spacing-md) !important;
                    text-align: center !important;
                }

                .header-nav {
                    flex-wrap: wrap !important;
                    justify-content: center !important;
                    gap: var(--spacing-sm) !important;
                    padding-top: var(--spacing-sm) !important;
                }

                .funding-logos {
                    justify-content: center !important;
                    gap: var(--spacing-xs) !important;
                    padding: var(--spacing-xs) var(--spacing-sm) !important;
                }

                .funding-logos img {
                    max-width: 40px !important;
                }

                .header-logo img {
                    height: 35px !important;
                }

                .header-nav a {
                    padding: var(--spacing-xs) var(--spacing-sm) !important;
                    font-size: var(--font-size-sm) !important;
                }
            }

            /* Force Pythia logo containers to have NO background (overrides all other CSS rules) */
            .persistent-header .header-logo,
            .persistent-header .header-logo *,
            .persistent-header div:has(> img[src*="Pythia"]),
            .persistent-header div:has(> img[src*="Logo"]),
            .persistent-header *:has(> img[src*="Pythia"]),
            .persistent-header *:has(> img[src*="Logo"]),
            .header-logo,
            .header-logo *,
            div.header-logo,
            div.header-logo *,
            html .persistent-header .header-logo,
            html .persistent-header div:has(> img[src*="Pythia"]),
            body .persistent-header .header-logo,
            body .persistent-header div:has(> img[src*="Pythia"]) {
                background: none !important;
                background-color: transparent !important;
                background-image: none !important;
                padding: 0 !important;
                margin: 0 !important;
                border: none !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                outline: none !important;
            }

            /* Ensure page content doesn't interfere with header navigation */
            #page-content {
                position: relative !important;
                z-index: 1 !important;
                padding-top: 0 !important;
            }

            /* Ensure home page centers properly without interfering with header */
            #page-content > div {
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                min-height: calc(100vh - 120px) !important;
                padding: var(--spacing-lg) !important;
            }

            /* Responsive results containers for desktop viewport adaptation */
            .results-container {
                max-width: 100% !important;
                margin: 0 auto !important;
                padding: var(--spacing-md) !important;
                overflow-x: auto !important;
            }

            /* Ensure tables and forms adapt to container width */
            .dash-table-container {
                max-width: 100% !important;
                overflow-x: auto !important;
            }

            /* Responsive form containers */
            .form-container {
                max-width: 1200px !important;
                margin: 0 auto !important;
                padding: 0 var(--spacing-md) !important;
            }

            /* Unified results container styling */
            .unified-results-container {
                background-color: var(--background-primary) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: var(--border-radius-lg) !important;
                box-shadow: var(--shadow-md) !important;
                padding: var(--spacing-xl) !important;
                margin: var(--spacing-lg) auto !important;
                width: 90% !important;
                max-width: 1100px !important;
                overflow-x: auto !important;
                box-sizing: border-box !important;
            }

            /* Results section headers */
            .results-header {
                font-size: var(--font-size-xl) !important;
                font-weight: 600 !important;
                color: var(--text-primary) !important;
                margin-bottom: var(--spacing-lg) !important;
                text-align: center !important;
            }

            /* Results heatmap container - no borders, seamless integration */
            .results-heatmap {
                margin: var(--spacing-lg) 0 !important;
                border: none !important;
                border-radius: var(--border-radius) !important;
                overflow: hidden !important;
            }

            /* Results table container */
            .results-table {
                margin-top: var(--spacing-xl) !important;
                border-radius: var(--border-radius) !important;
                overflow: hidden !important;
                box-shadow: var(--shadow-sm) !important;
            }

            /* Institution logos hover effects - REMOVED for static logos */

            /* Header containers for logos */
            div:has(> img[src*="Pythia.png"]) {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                position: relative !important;
            }

            /* Institution logos container styling */
            div:has(> img[src*="images.png"]) {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                flex-wrap: wrap !important;
                gap: var(--spacing-md) !important;
                padding: var(--spacing-xl) var(--spacing-2xl) !important;
            }

            /* Add subtle brand gradient behind main logos */
            div:has(> img[src*="Pythia.png"])::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120%;
                height: 120%;
                background: radial-gradient(ellipse at center, rgba(46, 91, 255, 0.03), transparent 70%);
                border-radius: var(--border-radius-xl);
                z-index: -1;
            }

            /* Page titles enhancement */
            h1 {
                position: relative !important;
                background: linear-gradient(135deg, var(--text-primary), var(--primary-color)) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
                text-shadow: none !important;
            }

            /* Fallback for browsers that don't support background-clip */
            @supports not (-webkit-background-clip: text) {
                h1 {
                    color: var(--text-primary) !important;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
                }
            }

            /* Enhanced main page title */
            .index-page h1 {
                font-size: var(--font-size-5xl) !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
                margin-bottom: var(--spacing-xl) !important;
                text-align: center !important;
            }

            /* Page headers for integration and editing */
            h1:not(.index-page h1) {
                font-size: var(--font-size-4xl) !important;
                font-weight: 700 !important;
                letter-spacing: -0.01em !important;
                margin: var(--spacing-xl) 0 var(--spacing-2xl) 0 !important;
            }

            /* Subtitle styling */
            p[style*="fontSize: '1.5em'"] {
                font-size: var(--font-size-xl) !important;
                color: var(--text-secondary) !important;
                font-weight: 400 !important;
                line-height: 1.5 !important;
                max-width: 800px !important;
                margin: 0 auto var(--spacing-xl) auto !important;
            }

            /* Enhanced Form Element Styling */

            /* Input field enhancements */
            input[type="text"],
            input[type="number"],
            input[type="email"],
            input[type="password"],
            textarea,
            select {
                background-color: var(--background-primary) !important;
                border: 2px solid var(--border-color) !important;
                border-radius: var(--border-radius-md) !important;
                padding: var(--spacing-md) var(--spacing-lg) !important;
                font-family: var(--font-family-primary) !important;
                font-size: var(--font-size-base) !important;
                line-height: 1.5 !important;
                color: var(--text-primary) !important;
                transition: all 0.2s ease-in-out !important;
                box-shadow: var(--shadow-sm) !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Hide DataTable total page count (the "32" number), keep navigation buttons */
            div.last-page {
                display: none !important;
            }

            /* DataTable pagination inputs - reset global overrides */
            input.current-page {
                width: 4ch !important;
                min-width: 4ch !important;
                max-width: 7ch !important;
                padding: 2px 4px !important;
                margin-bottom: 0 !important;
                box-sizing: content-box !important;
                color: var(--text-primary) !important;
                font-style: normal !important;
                transform: none !important;
                text-align: center !important;
            }
            input.current-page::placeholder {
                color: var(--text-secondary) !important;
                font-style: normal !important;
                opacity: 1 !important;
            }

            /* Input placeholder styling */
            input::placeholder,
            textarea::placeholder {
                color: var(--text-muted) !important;
                font-style: italic !important;
                opacity: 0.8 !important;
            }

            /* Input focus states */
            input[type="text"]:focus,
            input[type="number"]:focus,
            input[type="email"]:focus,
            input[type="password"]:focus,
            textarea:focus,
            select:focus {
                outline: none !important;
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(46, 91, 255, 0.1), var(--shadow-md) !important;
                background-color: var(--background-primary) !important;
                transform: translateY(-1px) !important;
            }

            /* Input hover states */
            input[type="text"]:hover,
            input[type="number"]:hover,
            input[type="email"]:hover,
            input[type="password"]:hover,
            textarea:hover,
            select:hover {
                border-color: var(--primary-color) !important;
                box-shadow: var(--shadow-md) !important;
            }

            /* Dropdown/Select specific styling */
            select {
                cursor: pointer !important;
                appearance: none !important;
                background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236B7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e") !important;
                background-position: right var(--spacing-md) center !important;
                background-repeat: no-repeat !important;
                background-size: 1.5em 1.5em !important;
                padding-right: calc(var(--spacing-lg) + 1.5em) !important;
            }

            /* Dash dropdown component styling */
            .Select-control {
                background-color: var(--background-primary) !important;
                border: 2px solid var(--border-color) !important;
                border-radius: var(--border-radius-md) !important;
                min-height: 48px !important;
                font-family: var(--font-family-primary) !important;
                font-size: var(--font-size-base) !important;
            }

            .Select-control:hover {
                border-color: var(--primary-color) !important;
                box-shadow: var(--shadow-md) !important;
            }

            .Select-control.is-focused {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(46, 91, 255, 0.1), var(--shadow-md) !important;
                outline: none !important;
            }

            .Select-value-label {
                color: var(--text-primary) !important;
                font-weight: 500 !important;
            }

            .Select-placeholder {
                color: var(--text-muted) !important;
                font-style: italic !important;
            }

            .Select-input > input {
                color: var(--text-primary) !important;
            }

            /* Force visibility for all dropdown input elements */
            .Select-input input,
            div[class*="Input"] input,
            div[class*="input"] input,
            #gene-dropdown-tagging input,
            #custom-tagging-species input,
            #custom-tagging-gene input,
            #custom-tagging-transcript input {
                color: #1F2937 !important;
                background-color: transparent !important;
                opacity: 1 !important;
                visibility: visible !important;
            }

            /* Form labels */
            label {
                font-family: var(--font-family-primary) !important;
                font-size: var(--font-size-sm) !important;
                font-weight: 600 !important;
                color: var(--text-primary) !important;
                margin-bottom: var(--spacing-xs) !important;
                display: block !important;
            }

            /* Form error states */
            input.error,
            select.error,
            textarea.error {
                border-color: var(--error-color) !important;
                box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1), var(--shadow-sm) !important;
            }

            /* Form success states */
            input.success,
            select.success,
            textarea.success {
                border-color: var(--success-color) !important;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1), var(--shadow-sm) !important;
            }

            /* Input groups and containers */
            .input-group {
                display: flex !important;
                gap: var(--spacing-md) !important;
                align-items: flex-end !important;
                margin-bottom: var(--spacing-lg) !important;
            }

            /* Number input specific styling */
            input[type="number"] {
                -moz-appearance: textfield !important;
            }

            input[type="number"]::-webkit-outer-spin-button,
            input[type="number"]::-webkit-inner-spin-button {
                -webkit-appearance: none !important;
                margin: 0 !important;
            }

            /* Textarea specific styling */
            textarea {
                resize: vertical !important;
                min-height: 120px !important;
                font-family: var(--font-family-mono) !important;
                font-size: var(--font-size-sm) !important;
                line-height: 1.6 !important;
            }

            /* File input styling */
            input[type="file"] {
                padding: var(--spacing-lg) !important;
                border: 2px dashed var(--border-color) !important;
                border-radius: var(--border-radius-md) !important;
                background-color: var(--background-secondary) !important;
                cursor: pointer !important;
                transition: all 0.2s ease-in-out !important;
            }

            input[type="file"]:hover {
                border-color: var(--primary-color) !important;
                background-color: var(--background-primary) !important;
            }

            /* Checkbox and radio styling */
            input[type="checkbox"],
            input[type="radio"] {
                width: 20px !important;
                height: 20px !important;
                margin-right: var(--spacing-sm) !important;
                cursor: pointer !important;
                accent-color: var(--primary-color) !important;
            }

            /* Form validation messages */
            .form-error-message {
                color: var(--error-color) !important;
                font-size: var(--font-size-sm) !important;
                margin-top: var(--spacing-xs) !important;
                display: block !important;
            }

            .form-success-message {
                color: var(--success-color) !important;
                font-size: var(--font-size-sm) !important;
                margin-top: var(--spacing-xs) !important;
                display: block !important;
            }

            /* Responsive form adjustments */
            @media (max-width: 768px) {
                .index-page img[src*="Pythia.png"] {
                    width: 40% !important;
                    min-width: 150px !important;
                    max-width: 200px !important;
                }

                div[style*="flex: '1'"] img[src*="Pythia.png"] {
                    height: 60px !important;
                    max-height: 60px !important;
                }

                .index-page h1 {
                    font-size: var(--font-size-4xl) !important;
                }

                img[src*="images.png"],
                img[src*="ERC.png"],
                img[src*="swiss.png"],
                img[src*="fwo.png"],
                img[src*="logo_UGent_EN_RGB_2400_color.png"],
                img[src*="uzh.png"] {
                    margin: var(--spacing-xs) var(--spacing-sm) !important;
                    max-width: 60px !important;
                    height: auto !important;
                }

                /* Mobile form adjustments */
                input[type="text"],
                input[type="number"],
                input[type="email"],
                input[type="password"],
                textarea,
                select {
                    font-size: 16px !important; /* Prevents zoom on iOS */
                    padding: var(--spacing-lg) !important;
                }

                .input-group {
                    flex-direction: column !important;
                    gap: var(--spacing-sm) !important;
                }
            }

            /* About link card hover effect */
            .about-link-card:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
                border-color: #D1D5DB !important;
            }

        </style>
        <script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def setup_layout(app):
    """Set up the common layout for the Dash app."""
    app.index_string = INDEX_STRING

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),

            # Store for tracking if user doesn't want to see modal again this session
            dcc.Store(id='dev-preview-session-store', storage_type='session', data={'show_modal': True}),

            # Development Preview Modal (global - appears on all pages)
            dbc.Modal([
                dbc.ModalHeader("Welcome to Pythia Development Preview"),
                dbc.ModalBody([
                    html.P("You've reached the development version of the Pythia platform. This preview is intended for article reviewers and internal testing purposes."),
                    html.P("Please note:", style={"fontWeight": "600", "marginTop": "1em", "marginBottom": "0.5em"}),
                    html.Ul([
                        html.Li(["The stable public release is available at ", html.A("pythia-editing.org", href="https://pythia-editing.org", target="_blank", style={"color": "#2E5BFF", "textDecoration": "underline"})]),
                        html.Li("This development version will be pushed to production hopefully in Q2 2026"),
                        html.Li("You're welcome to explore the new features, but be aware this is a pre-release environment")
                    ], style={"lineHeight": "1.8"}),
                    html.P("Thank you for your interest in Pythia!", style={"marginTop": "1em", "fontWeight": "500"}),
                    html.Div([
                        dcc.Checklist(
                            id="dev-preview-dont-show",
                            options=[{"label": " Don't show this again for this session", "value": "dont_show"}],
                            value=[],
                            style={"marginTop": "1em"}
                        )
                    ])
                ]),
                dbc.ModalFooter(
                    dbc.Button("I Understand", id="dev-preview-close", className="ms-auto", n_clicks=0, style={
                        "backgroundColor": "#2E5BFF",
                        "borderColor": "#2E5BFF",
                        "color": "white",
                        "padding": "0.5rem 2rem",
                        "fontSize": "1rem",
                        "fontWeight": "600"
                    })
                ),
            ],
            id="dev-preview-modal",
            is_open=True,
            centered=True,
            backdrop="static",
            keyboard=False,
            size="lg",
            style={"zIndex": "9999"}
            ),
        ],
        style={
            "backgroundColor": "white",
            "minHeight": "100vh",
            "margin": 0,
            "padding": 0
        },
    )


def create_header(current_page=None):
    """Create the persistent header with navigation menu"""
    return html.Div(
        className="persistent-header",
        children=[
            html.Div(
                className="header-grid",
                children=[
                    # Top row: Logo and Funding logos
                    html.Div(
                        className="header-top-row",
                        children=[
                            # Pythia logo on the left
                            html.Div(
                                className="header-logo",
                                children=[
                                    dcc.Link(
                                        html.Img(src="/assets/Landing/Logo/Pythia.png"),
                                        href="/",
                                        style={"textDecoration": "none"}
                                    )
                                ]
                            ),
                            # Funding logos on the right
                            html.Div(
                                className="funding-logos",
                                children=[
                                    html.Img(src="/assets/Landing/Logo/images.png"),
                                    html.Img(src="/assets/Landing/Logo/ERC.png"),
                                    html.Img(src="/assets/Landing/Logo/swiss.png"),
                                    html.Img(src="/assets/Landing/Logo/fwo.png", style={"width": "30px", "maxWidth": "30px", "height": "auto"}),
                                    html.Img(src="/assets/Landing/Logo/logo_UGent_EN_RGB_2400_color2.png", style={"width": "45px", "maxWidth": "45px", "height": "auto"}),
                                    html.Img(src="/assets/Landing/Logo/eth.png", style={"width": "45px", "maxWidth": "45px", "height": "auto"}),
                                    html.Img(src="/assets/Landing/Logo/uzh.png")
                                ]
                            )
                        ]
                    ),
                    # Bottom row: Navigation menu
                    html.Div(
                        className="header-nav",
                        children=[
                            dcc.Link(
                                "Home",
                                href="/",
                                refresh=False,
                                className="active" if current_page == "home" else ""
                            ),
                            dcc.Link(
                                "About",
                                href="/about",
                                refresh=False,
                                className="active" if current_page == "about" else ""
                            ),
                            dcc.Link(
                                "Integration",
                                href="/page-1",
                                refresh=False,
                                className="active" if current_page == "integration" else ""
                            ),
                            dcc.Link(
                                "Tagging",
                                href="/page-tagging",
                                refresh=False,
                                className="active" if current_page == "tagging" else ""
                            ),
                            dcc.Link(
                                "Editing",
                                href="/page-2",
                                refresh=False,
                                className="active" if current_page == "editing" else ""
                            ),
                            dcc.Link(
                                "Licenses",
                                href="/licenses",
                                refresh=False,
                                className="active" if current_page == "licenses" else ""
                            ),
                            dcc.Link(
                                "Team",
                                href="/team",
                                refresh=False,
                                className="active" if current_page == "team" else ""
                            ),
                            dcc.Link(
                                "Citation",
                                href="/citation",
                                refresh=False,
                                className="active" if current_page == "citation" else ""
                            ),
                            dcc.Link(
                                "Help",
                                href="/help",
                                refresh=False,
                                className="active" if current_page == "help" else ""
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_disclaimer():
    """Create the disclaimer footer to appear on all pages"""
    return html.P(
        [
            "Disclaimer: This tool and its content are provided strictly for academic research purposes only. Any application of the techniques, tools, or information provided here to purposes other than research, including but not limited to commercial use, therapeutic use or other clinical applications, is strictly prohibited. For more information, see our ",
            dcc.Link("Licenses", href="/licenses", style={"color": "#2E5BFF", "textDecoration": "underline"}),
            " page. Since we use pythonanywhere as our hosting provider, our data is transferred to the US by Amazon Web Services, which is certified under the EU-US Privacy Shield Framework. This provides certain safeguards in relation to the handling of your personal data. You can find pythonanywhere's privacy policy under https://www.pythonanywhere.com/privacy_v2/. This website does not implement any user analytics software."
        ],
        style={"color": "black", "fontSize": "0.8em", "textAlign": "center", "marginTop": "3em", "marginBottom": "2em", "padding": "0 2em"}
    )
