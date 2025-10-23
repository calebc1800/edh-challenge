// Theme toggle functionality

(function() {
    const THEME_KEY = 'mtg-deck-builder-theme';
    
    // Get saved theme or default to dark
    function getSavedTheme() {
        return localStorage.getItem(THEME_KEY) || 'dark';
    }
    
    // Save theme preference
    function saveTheme(theme) {
        localStorage.setItem(THEME_KEY, theme);
    }
    
    // Apply theme to document
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update button icon
        const themeToggle = document.getElementById('theme-toggle');
        const themeIcon = themeToggle.querySelector('.theme-icon');
        
        if (theme === 'light') {
            themeIcon.textContent = '☀️';
            themeToggle.title = 'Switch to dark mode';
        } else {
            themeIcon.textContent = '🌙';
            themeToggle.title = 'Switch to light mode';
        }
    }
    
    // Toggle between themes
    function toggleTheme() {
        const currentTheme = getSavedTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        saveTheme(newTheme);
        applyTheme(newTheme);
    }
    
    // Initialize theme on page load
    function initTheme() {
        const savedTheme = getSavedTheme();
        applyTheme(savedTheme);
        
        // Add click handler to toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }
    }
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();
