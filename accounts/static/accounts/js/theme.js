/**
 * SafeRoute Theme Toggle System
 * Handles light/dark mode switching with localStorage persistence
 */

(function() {
    'use strict';

    // Theme constants
    const THEME_KEY = 'saferoute-theme';
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark',
        SYSTEM: 'system'
    };

    // Theme Manager Object
    const ThemeManager = {
        /**
         * Initialize theme on page load
         */
        init: function() {
            // Load saved theme or default to system preference
            const savedTheme = this.getSavedTheme();
            const themeToApply = savedTheme || this.getSystemTheme();

            this.applyTheme(themeToApply);
            this.updateToggleButton(themeToApply);
            this.attachEventListeners();

            // Listen for system theme changes
            this.watchSystemTheme();
        },

        /**
         * Get saved theme from localStorage
         */
        getSavedTheme: function() {
            try {
                return localStorage.getItem(THEME_KEY);
            } catch (e) {
                console.warn('localStorage not available:', e);
                return null;
            }
        },

        /**
         * Save theme to localStorage
         */
        saveTheme: function(theme) {
            try {
                localStorage.setItem(THEME_KEY, theme);
            } catch (e) {
                console.warn('Could not save theme to localStorage:', e);
            }
        },

        /**
         * Get system theme preference
         */
        getSystemTheme: function() {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                return THEMES.DARK;
            }
            return THEMES.LIGHT;
        },

        /**
         * Apply theme to document
         */
        applyTheme: function(theme) {
            const effectiveTheme = theme === THEMES.SYSTEM ? this.getSystemTheme() : theme;

            if (effectiveTheme === THEMES.DARK) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }

            // Dispatch custom event for other scripts to listen to
            window.dispatchEvent(new CustomEvent('themechange', {
                detail: { theme: effectiveTheme }
            }));
        },

        /**
         * Toggle between light and dark themes
         */
        toggleTheme: function() {
            const currentTheme = this.getSavedTheme() || THEMES.LIGHT;
            const newTheme = currentTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;

            this.applyTheme(newTheme);
            this.saveTheme(newTheme);
            this.updateToggleButton(newTheme);

            // Add animation effect
            this.animateThemeChange();
        },

        /**
         * Update toggle button icon and aria-label
         */
        updateToggleButton: function(theme) {
            const button = document.getElementById('theme-toggle');
            if (!button) return;

            const icon = button.querySelector('i');
            const effectiveTheme = theme === THEMES.SYSTEM ? this.getSystemTheme() : theme;

            if (effectiveTheme === THEMES.DARK) {
                icon.className = 'bi bi-sun-fill';
                button.setAttribute('aria-label', 'Switch to light mode');
                button.setAttribute('title', 'Switch to light mode');
            } else {
                icon.className = 'bi bi-moon-stars-fill';
                button.setAttribute('aria-label', 'Switch to dark mode');
                button.setAttribute('title', 'Switch to dark mode');
            }
        },

        /**
         * Attach event listeners
         */
        attachEventListeners: function() {
            const button = document.getElementById('theme-toggle');
            if (button) {
                button.addEventListener('click', () => this.toggleTheme());
            }
        },

        /**
         * Watch for system theme changes
         */
        watchSystemTheme: function() {
            if (!window.matchMedia) return;

            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

            // Modern browsers
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', (e) => {
                    // Only apply if user hasn't set a preference
                    if (!this.getSavedTheme()) {
                        this.applyTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
                        this.updateToggleButton(e.matches ? THEMES.DARK : THEMES.LIGHT);
                    }
                });
            }
            // Fallback for older browsers
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener((e) => {
                    if (!this.getSavedTheme()) {
                        this.applyTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
                        this.updateToggleButton(e.matches ? THEMES.DARK : THEMES.LIGHT);
                    }
                });
            }
        },

        /**
         * Add visual animation when theme changes
         */
        animateThemeChange: function() {
            document.body.style.transition = 'none';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 50);
        },

        /**
         * Get current active theme
         */
        getCurrentTheme: function() {
            return document.documentElement.hasAttribute('data-theme') ? THEMES.DARK : THEMES.LIGHT;
        }
    };

    // Initialize theme when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
    } else {
        ThemeManager.init();
    }

    // Expose ThemeManager globally for debugging/testing
    window.ThemeManager = ThemeManager;

})();
