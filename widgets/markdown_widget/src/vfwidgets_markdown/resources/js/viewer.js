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

        console.log('[MarkdownViewer] markdown-it initialized');
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
    render(markdown) {
        console.log(`[MarkdownViewer] Rendering ${markdown.length} bytes`);

        try {
            // Clear previous content
            const contentDiv = document.getElementById('content');
            const errorDiv = document.getElementById('error');
            errorDiv.style.display = 'none';

            // Render markdown to HTML
            const html = this.md.render(markdown);
            contentDiv.innerHTML = html;

            // Post-process for special features
            this.processMermaid();
            this.processKaTeX();
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
    processMermaid() {
        if (typeof mermaid === 'undefined') return;

        const mermaidBlocks = document.querySelectorAll('code.language-mermaid');
        console.log(`[MarkdownViewer] Processing ${mermaidBlocks.length} Mermaid diagrams`);

        mermaidBlocks.forEach((block, index) => {
            const code = block.textContent;
            const id = `mermaid-${Date.now()}-${index}`;

            try {
                // Create container for diagram
                const container = document.createElement('div');
                container.className = 'mermaid-diagram';
                container.id = id;
                container.textContent = code;

                // Replace code block with diagram container
                block.parentElement.replaceWith(container);

                // Render diagram
                mermaid.init(undefined, container);
            } catch (error) {
                console.error('Mermaid rendering failed:', error);
                block.parentElement.innerHTML = `<pre style="color: red;">Mermaid Error: ${error.message}</pre>`;
            }
        });
    },

    /**
     * Process KaTeX math equations
     */
    processKaTeX() {
        if (typeof katex === 'undefined') return;

        // Process inline math: $...$
        const content = document.getElementById('content');
        const mathInline = content.querySelectorAll('code');

        mathInline.forEach(code => {
            const text = code.textContent;
            if (text.startsWith('$') && text.endsWith('$') && text.length > 2) {
                try {
                    const mathText = text.slice(1, -1);
                    const span = document.createElement('span');
                    katex.render(mathText, span, { displayMode: false });
                    code.replaceWith(span);
                } catch (e) {
                    console.warn('KaTeX inline failed:', e);
                }
            }
        });

        // Process block math: $$...$$
        const mathBlocks = content.querySelectorAll('pre code');
        mathBlocks.forEach(code => {
            const text = code.textContent.trim();
            if (text.startsWith('$$') && text.endsWith('$$')) {
                try {
                    const mathText = text.slice(2, -2).trim();
                    const div = document.createElement('div');
                    div.style.textAlign = 'center';
                    div.style.margin = '20px 0';
                    katex.render(mathText, div, { displayMode: true });
                    code.parentElement.replaceWith(div);
                } catch (e) {
                    console.warn('KaTeX block failed:', e);
                }
            }
        });

        console.log('[MarkdownViewer] KaTeX processing complete');
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
    setTheme(theme) {
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

        // Update Mermaid theme
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                theme: theme === 'dark' ? 'dark' : 'default'
            });
            // Re-render mermaid diagrams
            const mermaidDivs = document.querySelectorAll('.mermaid-diagram');
            mermaidDivs.forEach(div => {
                mermaid.init(undefined, div);
            });
        }
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
