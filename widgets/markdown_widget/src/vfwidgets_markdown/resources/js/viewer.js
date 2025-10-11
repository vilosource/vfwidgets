/**
 * Markdown Viewer - JavaScript Rendering Engine
 *
 * This module handles all markdown rendering, diagram generation,
 * syntax highlighting, and communication with the Python/Qt layer.
 */

// Global state
const MarkdownViewer = {
    md: null,
    qtBridge: null,
    currentTheme: 'light',
    scrollPosition: 0,
    shortcutsEnabled: false,
    customShortcuts: {},
    currentZoom: 1.0,

    /**
     * Initialize the markdown viewer
     */
    init() {
        console.log('[MarkdownViewer] Initializing...');

        // Initialize markdown-it
        this.initMarkdownIt();

        // Initialize Mermaid
        this.initMermaid();

        // Initialize Prism
        this.initPrism();

        // Setup QWebChannel bridge
        this.setupBridge();

        // Setup editor integration
        this.setupEditorIntegration();

        console.log('[MarkdownViewer] Initialization complete');
        document.getElementById('loading').style.display = 'none';
    },

    /**
     * Initialize markdown-it parser with plugins
     */
    initMarkdownIt() {
        this.md = window.markdownit({
            html: true,          // Enable HTML tags
            linkify: true,       // Auto-convert URLs to links
            typographer: true,   // Smart quotes, dashes
            breaks: false,       // Don't convert \n to <br>
            highlight: (code, lang) => {
                // Delegate to Prism for syntax highlighting
                if (lang && Prism.languages[lang]) {
                    try {
                        return Prism.highlight(code, Prism.languages[lang], lang);
                    } catch (e) {
                        console.warn('Prism highlighting failed:', e);
                    }
                }
                return code; // Fallback to plain text
            }
        });

        // Load markdown-it plugins for extended syntax
        // Note: Order matters for some plugins

        // Footnotes, abbreviations, definition lists - these are safe
        if (typeof markdownitFootnote !== 'undefined') {
            this.md.use(markdownitFootnote);
            console.log('[MarkdownViewer] Loaded footnote plugin');
        }

        if (typeof markdownitAbbr !== 'undefined') {
            this.md.use(markdownitAbbr);
            console.log('[MarkdownViewer] Loaded abbreviation plugin');
        }

        if (typeof markdownitDeflist !== 'undefined') {
            this.md.use(markdownitDeflist);
            console.log('[MarkdownViewer] Loaded definition list plugin');
        }

        // Task lists (checkboxes)
        if (typeof markdownitTaskLists !== 'undefined') {
            this.md.use(markdownitTaskLists);
            console.log('[MarkdownViewer] Loaded task lists plugin');
        }

        // Container plugin for custom blocks (:::warning, etc.)
        if (typeof markdownitContainer !== 'undefined') {
            // Register common containers
            ['warning', 'info', 'danger', 'tip', 'note'].forEach(name => {
                this.md.use(markdownitContainer, name, {
                    render: (tokens, idx) => {
                        if (tokens[idx].nesting === 1) {
                            return `<div class="${name}">\n`;
                        } else {
                            return '</div>\n';
                        }
                    }
                });
            });
            console.log('[MarkdownViewer] Loaded container plugin');
        }

        // Override validateLink to allow data: URIs for images
        // By default, markdown-it blocks data: URIs for security
        const defaultValidateLink = this.md.validateLink.bind(this.md);
        this.md.validateLink = function(url) {
            // Allow data: URIs (for base64 images)
            if (url.startsWith('data:')) {
                return true;
            }
            // Use default validation for other URLs
            return defaultValidateLink(url);
        };

        console.log('[MarkdownViewer] markdown-it initialized with data: URI support and plugins');
    },

    /**
     * Initialize Mermaid for diagram rendering
     */
    initMermaid() {
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,  // Manual rendering
                theme: 'default',
                securityLevel: 'loose',
                logLevel: 'error'
            });
            console.log('[MarkdownViewer] Mermaid initialized');
        } else {
            console.warn('[MarkdownViewer] Mermaid not loaded');
        }
    },

    /**
     * Initialize Prism for syntax highlighting
     */
    initPrism() {
        if (typeof Prism !== 'undefined') {
            // Configure Prism autoloader
            if (Prism.plugins && Prism.plugins.autoloader) {
                Prism.plugins.autoloader.languages_path = 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/';
            }
            console.log('[MarkdownViewer] Prism initialized');
        } else {
            console.warn('[MarkdownViewer] Prism not loaded');
        }
    },

    /**
     * Setup QWebChannel bridge for Python communication
     */
    setupBridge() {
        if (typeof QWebChannel === 'undefined') {
            console.warn('[MarkdownViewer] QWebChannel not available');
            return;
        }

        new QWebChannel(qt.webChannelTransport, (channel) => {
            this.qtBridge = channel.objects.qtBridge;
            console.log('[MarkdownViewer] Qt bridge connected');

            // Notify Python that viewer is ready
            this.sendMessage({ type: 'ready' });
        });
    },

    /**
     * Render markdown content
     * @param {string} markdown - Markdown text to render
     */
    async render(markdown) {
        console.log(`[MarkdownViewer] Rendering ${markdown.length} bytes`);

        try {
            // Clear previous content
            const contentDiv = document.getElementById('content');
            const errorDiv = document.getElementById('error');
            errorDiv.style.display = 'none';

            // Render markdown to HTML
            const html = this.md.render(markdown);
            contentDiv.innerHTML = html;

            // Post-process for special features (Mermaid must be awaited)
            await this.processMermaid();
            this.highlightCode();
            this.addHeadingIds();

            // Extract TOC
            const toc = this.extractTOC();

            // Notify Python
            this.sendMessage({ type: 'content_loaded' });
            this.sendMessage({ type: 'toc_changed', data: toc });

            console.log('[MarkdownViewer] Rendering complete');
        } catch (error) {
            this.showError(error);
        }
    },

    /**
     * Process Mermaid diagram blocks
     */
    async processMermaid() {
        if (typeof mermaid === 'undefined') return;

        const mermaidBlocks = document.querySelectorAll('code.language-mermaid');
        console.log(`[MarkdownViewer] Processing ${mermaidBlocks.length} Mermaid diagrams`);

        // Process each diagram sequentially to avoid conflicts
        for (let index = 0; index < mermaidBlocks.length; index++) {
            const block = mermaidBlocks[index];
            const code = block.textContent;
            const id = `mermaid-${Date.now()}-${index}`;

            try {
                // Use mermaid.render() API which is more reliable
                const { svg } = await mermaid.render(id, code);

                // Create container for diagram
                const container = document.createElement('div');
                container.className = 'mermaid-diagram';
                container.innerHTML = svg;

                // Replace code block with rendered diagram
                block.parentElement.replaceWith(container);

                console.log(`[MarkdownViewer] Rendered Mermaid diagram ${index + 1}/${mermaidBlocks.length}`);
            } catch (error) {
                console.error('Mermaid rendering failed:', error);
                const errorDiv = document.createElement('pre');
                errorDiv.style.color = 'red';
                errorDiv.style.padding = '10px';
                errorDiv.style.border = '1px solid red';
                errorDiv.textContent = `Mermaid Error: ${error.message}\n\nCode:\n${code}`;
                block.parentElement.replaceWith(errorDiv);
            }
        }
    },

    /**
     * Highlight code blocks with Prism
     */
    highlightCode() {
        if (typeof Prism === 'undefined') return;

        Prism.highlightAll();
        console.log('[MarkdownViewer] Prism highlighting complete');
    },

    /**
     * Add IDs to headings for navigation
     */
    addHeadingIds() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach((heading, index) => {
            if (!heading.id) {
                // Generate ID from text content
                const text = heading.textContent.trim();
                const id = text.toLowerCase()
                    .replace(/[^\w\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/--+/g, '-')
                    || `heading-${index}`;
                heading.id = id;
            }
        });
    },

    /**
     * Extract table of contents from headings
     * @returns {Array} TOC data
     */
    extractTOC() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const toc = [];

        headings.forEach(heading => {
            // Get text content and clean it thoroughly
            let text = heading.textContent.trim();

            // Remove any markdown heading markers that might have leaked through
            text = text.replace(/^#+\s*/, '');

            // Remove any trailing markers
            text = text.replace(/\s*#+$/, '');

            toc.push({
                level: parseInt(heading.tagName[1]),
                text: text,
                id: heading.id,
                line: 0  // Line numbers would require markdown-it plugin
            });
        });

        console.log(`[MarkdownViewer] Extracted TOC with ${toc.length} headings`);
        return toc;
    },

    /**
     * Set theme (light/dark)
     * @param {string} theme - Theme name
     */
    async setTheme(theme) {
        console.log(`[MarkdownViewer] Setting theme: ${theme}`);
        this.currentTheme = theme;
        document.body.dataset.theme = theme;

        // Switch Prism theme
        const prismTheme = document.getElementById('prism-theme');
        if (theme === 'dark') {
            prismTheme.href = 'css/prism-themes/prism-vscode-dark.css';
        } else {
            prismTheme.href = 'css/prism-themes/prism.css';
        }

        // Update Mermaid theme by re-initializing and re-rendering all diagrams
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: theme === 'dark' ? 'dark' : 'default',
                securityLevel: 'loose',
                logLevel: 'error'
            });

            // Note: Theme change requires re-rendering from markdown source
            // This is handled by the application calling render() again if needed
            console.log(`[MarkdownViewer] Mermaid theme updated to: ${theme === 'dark' ? 'dark' : 'default'}`);
        }
    },

    /**
     * Set syntax theme independently of main theme
     * @param {string} theme - Prism theme name (e.g., 'prism', 'prism-vscode-dark')
     */
    setSyntaxTheme(theme) {
        console.log(`[MarkdownViewer] Setting syntax theme: ${theme}`);
        const prismTheme = document.getElementById('prism-theme');
        prismTheme.href = `css/prism-themes/${theme}.css`;
    },

    /**
     * Scroll to heading by ID
     * @param {string} id - Heading ID
     */
    scrollToHeading(id) {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            console.log(`[MarkdownViewer] Scrolled to heading: ${id}`);
        }
    },

    /**
     * Send message to Python layer
     * @param {object} message - Message object
     */
    sendMessage(message) {
        if (this.qtBridge && this.qtBridge.receiveMessage) {
            this.qtBridge.receiveMessage(JSON.stringify(message));
        }
    },

    /**
     * Get current scroll position (0.0 to 1.0)
     * @returns {number} Scroll position as percentage
     */
    getScrollPosition() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        return scrollHeight > 0 ? scrollTop / scrollHeight : 0;
    },

    /**
     * Set scroll position (0.0 to 1.0)
     * @param {number} position - Target scroll position as percentage
     */
    setScrollPosition(position) {
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollTop = position * scrollHeight;
        window.scrollTo(0, scrollTop);
        console.log(`[MarkdownViewer] Scroll position set to ${(position * 100).toFixed(1)}%`);
    },

    /**
     * Setup editor integration features
     */
    setupEditorIntegration() {
        // Track scroll position changes
        let scrollTimeout = null;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }

            scrollTimeout = setTimeout(() => {
                const position = this.getScrollPosition();
                this.sendMessage({
                    type: 'scroll_position_changed',
                    position: position
                });
            }, 100);  // Throttle scroll events to every 100ms
        });

        // Track heading clicks
        document.addEventListener('click', (event) => {
            const target = event.target;

            // Check if clicked element is a heading
            if (target.tagName && target.tagName.match(/^H[1-6]$/)) {
                const headingId = target.id;
                if (headingId) {
                    this.sendMessage({
                        type: 'heading_clicked',
                        heading_id: headingId
                    });
                    console.log(`[MarkdownViewer] Heading clicked: ${headingId}`);
                }
            }

            // Check if clicked element is a link
            if (target.tagName === 'A' && target.href) {
                const href = target.href;
                // Only emit for non-heading anchor links
                if (!href.startsWith('#')) {
                    event.preventDefault();  // Prevent default navigation
                    this.sendMessage({
                        type: 'link_clicked',
                        url: href
                    });
                    console.log(`[MarkdownViewer] Link clicked: ${href}`);
                }
            }
        });

        console.log('[MarkdownViewer] Editor integration features enabled');
    },

    /**
     * Enable or disable keyboard shortcuts
     * @param {boolean} enabled - Enable/disable shortcuts
     */
    enableShortcuts(enabled) {
        this.shortcutsEnabled = enabled;

        if (enabled) {
            this.setupKeyboardShortcuts();
        }

        console.log(`[MarkdownViewer] Keyboard shortcuts ${enabled ? 'enabled' : 'disabled'}`);
    },

    /**
     * Set custom keyboard shortcuts
     * @param {Object} shortcuts - Custom shortcut mappings
     */
    setCustomShortcuts(shortcuts) {
        this.customShortcuts = shortcuts;
        console.log(`[MarkdownViewer] Set ${Object.keys(shortcuts).length} custom shortcuts`);
    },

    /**
     * Setup keyboard shortcut event handlers
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            if (!this.shortcutsEnabled) return;

            const key = event.key;
            const ctrl = event.ctrlKey || event.metaKey;  // Cmd on Mac, Ctrl on others
            const shift = event.shiftKey;
            const alt = event.altKey;

            // Build key combination string
            let combo = '';
            if (ctrl) combo += 'Ctrl+';
            if (shift) combo += 'Shift+';
            if (alt) combo += 'Alt+';
            combo += key;

            // Check custom shortcuts first
            if (this.customShortcuts[combo]) {
                event.preventDefault();
                this.sendMessage({
                    type: 'shortcut_triggered',
                    action: this.customShortcuts[combo],
                    combo: combo
                });
                return;
            }

            // Built-in shortcuts
            // Find: Ctrl/Cmd+F
            if (ctrl && key === 'f') {
                event.preventDefault();
                this.showFind();
                return;
            }

            // Zoom in: Ctrl/Cmd+Plus or Ctrl/Cmd+=
            if (ctrl && (key === '+' || key === '=')) {
                event.preventDefault();
                this.zoomIn();
                return;
            }

            // Zoom out: Ctrl/Cmd+Minus or Ctrl/Cmd+-
            if (ctrl && (key === '-' || key === '_')) {
                event.preventDefault();
                this.zoomOut();
                return;
            }

            // Reset zoom: Ctrl/Cmd+0
            if (ctrl && key === '0') {
                event.preventDefault();
                this.resetZoom();
                return;
            }

            // Scroll to top: Home
            if (key === 'Home' && !ctrl) {
                event.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
                return;
            }

            // Scroll to bottom: End
            if (key === 'End' && !ctrl) {
                event.preventDefault();
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                return;
            }

            // Page up
            if (key === 'PageUp') {
                event.preventDefault();
                window.scrollBy({ top: -window.innerHeight * 0.9, behavior: 'smooth' });
                return;
            }

            // Page down
            if (key === 'PageDown') {
                event.preventDefault();
                window.scrollBy({ top: window.innerHeight * 0.9, behavior: 'smooth' });
                return;
            }

            // Escape: Clear selection
            if (key === 'Escape') {
                window.getSelection().removeAllRanges();
                return;
            }
        });

        console.log('[MarkdownViewer] Keyboard shortcuts initialized');
    },

    /**
     * Show find dialog (browser native)
     */
    showFind() {
        // Trigger browser's native find
        document.execCommand('find');
        console.log('[MarkdownViewer] Find triggered');
    },

    /**
     * Zoom in
     */
    zoomIn() {
        this.currentZoom = Math.min(this.currentZoom + 0.1, 3.0);
        document.body.style.zoom = this.currentZoom;
        console.log(`[MarkdownViewer] Zoom: ${(this.currentZoom * 100).toFixed(0)}%`);
    },

    /**
     * Zoom out
     */
    zoomOut() {
        this.currentZoom = Math.max(this.currentZoom - 0.1, 0.5);
        document.body.style.zoom = this.currentZoom;
        console.log(`[MarkdownViewer] Zoom: ${(this.currentZoom * 100).toFixed(0)}%`);
    },

    /**
     * Reset zoom
     */
    resetZoom() {
        this.currentZoom = 1.0;
        document.body.style.zoom = this.currentZoom;
        console.log('[MarkdownViewer] Zoom reset to 100%');
    },

    /**
     * Get rendered HTML content
     * @returns {string} Rendered HTML
     */
    getRenderedHTML() {
        const contentDiv = document.getElementById('content');
        return contentDiv.innerHTML;
    },

    /**
     * Get full HTML document with styles
     * @returns {string} Complete HTML document
     */
    getFullHTML() {
        const contentDiv = document.getElementById('content');
        const styles = this.collectStyles();

        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exported Markdown</title>
    <style>
${styles}
    </style>
</head>
<body data-theme="${this.currentTheme}">
    <div id="content">
${contentDiv.innerHTML}
    </div>
</body>
</html>`;
    },

    /**
     * Collect all CSS styles for export
     * @returns {string} Combined CSS
     */
    collectStyles() {
        let styles = '';

        // Get inline styles from style tags
        const styleTags = document.querySelectorAll('style');
        styleTags.forEach(tag => {
            styles += tag.textContent + '\n';
        });

        // Get linked stylesheets content (from same origin)
        const linkTags = document.querySelectorAll('link[rel="stylesheet"]');
        linkTags.forEach(link => {
            try {
                if (link.sheet && link.sheet.cssRules) {
                    for (let rule of link.sheet.cssRules) {
                        styles += rule.cssText + '\n';
                    }
                }
            } catch (e) {
                console.warn('[MarkdownViewer] Could not access stylesheet:', link.href);
            }
        });

        return styles;
    },

    /**
     * Show error message
     * @param {Error} error - Error object
     */
    showError(error) {
        console.error('[MarkdownViewer] Error:', error);
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.style.display = 'block';

        this.sendMessage({
            type: 'rendering_failed',
            error: error.message
        });
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MarkdownViewer.init());
} else {
    MarkdownViewer.init();
}

// Expose to global scope for Python to call
window.MarkdownViewer = MarkdownViewer;
