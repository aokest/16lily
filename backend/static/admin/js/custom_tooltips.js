document.addEventListener('DOMContentLoaded', function() {
    // Function to convert help text to tooltips
    function initTooltips() {
        // Common selectors for help text in Django Admin / Jazzmin
        // Standard Django: .help
        // Jazzmin/Bootstrap: .form-text, .help-block
        const helpSelectors = ['.help', '.form-text', '.help-block'];
        
        helpSelectors.forEach(selector => {
            const helpElements = document.querySelectorAll(selector);
            
            helpElements.forEach(el => {
                // Avoid processing twice
                if (el.classList.contains('original-help-text-hidden') || el.querySelector('.custom-tooltip-icon')) {
                    return;
                }
                
                const text = el.textContent.trim();
                if (!text) return;

                // Create Icon
                const icon = document.createElement('i');
                // Use FontAwesome if available (Jazzmin), otherwise a simple span
                icon.className = 'fas fa-question-circle custom-tooltip-icon';
                if (!document.querySelector('link[href*="fontawesome"]')) {
                     // Fallback if no fontawesome
                     icon.className = 'custom-tooltip-icon';
                     icon.textContent = '?';
                     icon.style.fontWeight = 'bold';
                     icon.style.border = '1px solid #17a2b8';
                     icon.style.borderRadius = '50%';
                     icon.style.width = '16px';
                     icon.style.height = '16px';
                     icon.style.textAlign = 'center';
                     icon.style.lineHeight = '14px';
                }
                
                icon.setAttribute('data-tooltip', text);
                
                // Find the label to append the icon to
                // Structure usually: 
                // <div class="form-group"> <label>Text</label> ... <div class="help">...</div> </div>
                // We want the icon NEXT TO THE LABEL or INPUT.
                // User requested: "Next to these financial indicators... small question mark"
                
                // Try to find the preceding label in the same container
                const formGroup = el.closest('.form-group, .form-row');
                let label = null;
                if (formGroup) {
                    label = formGroup.querySelector('label');
                }
                
                if (label) {
                    label.appendChild(icon);
                    // Hide original
                    el.classList.add('original-help-text-hidden');
                } else {
                    // Fallback: Insert before the help text
                    el.parentNode.insertBefore(icon, el);
                    el.classList.add('original-help-text-hidden');
                }
            });
        });
    }

    // Run initialization
    initTooltips();

    // Observer for dynamic content (if any, though Admin is mostly static)
    // But let's check for DatePicker
    
    // DatePicker Fix: Ensure calendar icon is visible if vDateField is present
    // Django's DateTimeShortcuts should handle this, but if we need to trigger it manually:
    if (window.DateTimeShortcuts) {
        // DateTimeShortcuts.init(); // Usually runs on load
    }
    
    // If user wants natural language + calendar:
    // The calendar widget writes to the input. The input is just text.
    // So typing "20250204" is fine. The calendar picker will overwrite it if used.
    // My clean method handles the text.
});
