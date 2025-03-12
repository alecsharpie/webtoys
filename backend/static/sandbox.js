/**
 * WebToy Sandbox Manager
 * 
 * This module handles the secure rendering of WebToy code in a sandboxed environment.
 * It uses iframe sandboxing and Content Security Policy to restrict capabilities.
 */

class WebToySandbox {
    constructor(containerSelector) {
      this.container = document.querySelector(containerSelector);
      if (!this.container) {
        throw new Error(`Container not found: ${containerSelector}`);
      }
      
      this.iframe = null;
      this.webToyCode = null;
    }
    
    /**
     * Load a WebToy in the sandbox
     * @param {Object} webToyCode - Object containing HTML, CSS, and JS code
     * @param {Object} options - Configuration options
     */
    loadWebToy(webToyCode, options = {}) {
      this.webToyCode = webToyCode;
      
      // Store the original code
      this._createSandbox();
      this._injectCode(webToyCode, options);
      
      return this;
    }
    
    /**
     * Create a sandboxed iframe environment
     * @private
     */
    _createSandbox() {
      // Remove any existing iframe
      if (this.iframe) {
        this.iframe.remove();
      }
      
      // Create a new iframe with sandbox restrictions
      this.iframe = document.createElement('iframe');
      this.iframe.setAttribute('sandbox', 'allow-scripts');
      this.iframe.setAttribute('class', 'webtoy-sandbox');
      this.iframe.setAttribute('frameborder', '0');
      this.iframe.setAttribute('width', '100%');
      this.iframe.setAttribute('height', '100%');
      
      // Set initial source to about:blank
      this.iframe.setAttribute('src', 'about:blank');
      
      // Add to container
      this.container.appendChild(this.iframe);
      
      return this.iframe;
    }
    
    /**
     * Inject WebToy code into the sandboxed iframe
     * @param {Object} code - Object containing HTML, CSS, and JS code
     * @param {Object} options - Configuration options
     * @private
     */
    _injectCode(code, options = {}) {
      // Wait for iframe to load
      this.iframe.onload = () => {
        // Get reference to iframe document
        const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
        
        // Create content with security measures
        const content = this._createSecureContent(code, options);
        
        // Write content to iframe
        iframeDoc.open();
        iframeDoc.write(content);
        iframeDoc.close();
        
        // Set up message listener for controlled communication
        this._setupMessageListener();
      };
    }
    
    /**
     * Create secure HTML content with appropriate restrictions
     * @param {Object} code - Object containing HTML, CSS, and JS code
     * @param {Object} options - Configuration options
     * @private
     */
    _createSecureContent(code, options = {}) {
      const { html, css, js } = code;
      const title = options.title || 'WebToy';
      
      // Create a complete HTML document with security headers
      return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${this._escapeHtml(title)}</title>
          
          <!-- Content Security Policy to restrict capabilities -->
          <meta http-equiv="Content-Security-Policy" content="
            default-src 'none';
            script-src 'unsafe-inline';
            style-src 'unsafe-inline';
            img-src data: 'self';
            connect-src 'none';
            font-src 'none';
            object-src 'none';
            media-src 'none';
            form-action 'none';
            base-uri 'none';
          ">
          
          <!-- Custom styles -->
          <style>
            body {
              margin: 0;
              padding: 0;
              overflow: hidden;
              background: transparent;
            }
            canvas {
              display: block;
            }
            ${css || ''}
          </style>
        </head>
        <body>
          <!-- WebToy HTML -->
          ${html || ''}
          
          <!-- Security wrapper around script execution -->
          <script>
            // Error handling wrapper
            try {
              // WebToy code
              (function() {
                "use strict";
                // Block access to parent window
                window.parent = undefined;
                window.top = undefined;
                
                // Block common dangerous globals
                window.localStorage = undefined;
                window.sessionStorage = undefined;
                window.indexedDB = undefined;
                window.webkitIndexedDB = undefined;
                window.mozIndexedDB = undefined;
                window.msIndexedDB = undefined;
                window.location = undefined;
                
                // Isolated WebToy code
                ${js || ''}
              })();
            } catch (error) {
              // Handle errors gracefully
              console.error('WebToy error:', error);
              document.body.innerHTML = '<div style="padding: 20px; color: red;">Error: ' + error.message + '</div>';
            }
          </script>
        </body>
        </html>
      `;
    }
    
    /**
     * Set up a controlled message listener for iframe communication
     * @private
     */
    _setupMessageListener() {
      window.addEventListener('message', (event) => {
        // Only accept messages from our iframe
        if (event.source !== this.iframe.contentWindow) {
          return;
        }
        
        // Process allowed messages...
        // (In this simplified version, we're not implementing any message passing)
      });
    }
    
    /**
     * Helper function to escape HTML entities
     * @param {string} html - String to escape
     * @private
     */
    _escapeHtml(html) {
      const div = document.createElement('div');
      div.textContent = html;
      return div.innerHTML;
    }
  }
  
  // Export for use in the application
  window.WebToySandbox = WebToySandbox;