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

        // Anchor plugin (must be loaded first for TOC)
        if (typeof markdownItAnchor !== 'undefined') {
            this.md.use(markdownItAnchor.default || markdownItAnchor, {
                permalink: false,
                level: [1, 2, 3, 4, 5, 6]
            });
            console.log('[MarkdownViewer] Loaded anchor plugin');
        }

        // Footnotes
        if (typeof markdownitFootnote !== 'undefined') {
            this.md.use(markdownitFootnote);
            console.log('[MarkdownViewer] Loaded footnote plugin');
        }

        // Abbreviations
        if (typeof markdownitAbbr !== 'undefined') {
            this.md.use(markdownitAbbr);
            console.log('[MarkdownViewer] Loaded abbreviation plugin');
        }

        // Definition lists
        if (typeof markdownitDeflist !== 'undefined') {
            this.md.use(markdownitDeflist);
            console.log('[MarkdownViewer] Loaded definition list plugin');
        }

        // Text formatting
        if (typeof markdownitMark !== 'undefined') {
            this.md.use(markdownitMark);
            console.log('[MarkdownViewer] Loaded mark (highlight) plugin');
        }
        if (typeof markdownitSub !== 'undefined') {
            this.md.use(markdownitSub);
            console.log('[MarkdownViewer] Loaded subscript plugin');
        }
        if (typeof markdownitSup !== 'undefined') {
            this.md.use(markdownitSup);
            console.log('[MarkdownViewer] Loaded superscript plugin');
        }
        if (typeof markdownitIns !== 'undefined') {
            this.md.use(markdownitIns);
            console.log('[MarkdownViewer] Loaded insert plugin');
        }

        // Emoji
        if (typeof markdownitEmoji !== 'undefined') {
            this.md.use(markdownitEmoji);
            console.log('[MarkdownViewer] Loaded emoji plugin');
        }

        // Task lists
        if (typeof markdownitTaskLists !== 'undefined') {
            this.md.use(markdownitTaskLists, {
                enabled: true,
                label: true,
                labelAfter: true
            });
            console.log('[MarkdownViewer] Loaded task lists plugin');
        }

        // Custom containers (warning, info, danger, etc.)
        if (typeof markdownitContainer !== 'undefined') {
            // Define common container types
            this.md.use(markdownitContainer, 'warning');
            this.md.use(markdownitContainer, 'info');
            this.md.use(markdownitContainer, 'danger');
            this.md.use(markdownitContainer, 'tip');
            this.md.use(markdownitContainer, 'note');
            console.log('[MarkdownViewer] Loaded container plugin');
        }

        // Math rendering with KaTeX
        if (typeof markdownitKatex !== 'undefined' && typeof katex !== 'undefined') {
            this.md.use(markdownitKatex);
            console.log('[MarkdownViewer] Loaded KaTeX plugin');
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
            toc.push({
                level: parseInt(heading.tagName[1]),
                text: heading.textContent.trim(),
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
