document.addEventListener('DOMContentLoaded', function() {
    console.log("Opportunity Log JS Loaded (Enhanced Select)");
    
    // Function to handle action field visibility logic
    function toggleActionFields(selectElement) {
        if (!selectElement) return;
        
        const selectedValue = selectElement.value;
        const formRow = selectElement.closest('.form-row') || selectElement.closest('tr'); // standard or inline
        
        // Find the 'action' (text input) field
        // In standard form, it's a sibling row .field-action
        // In our custom form layout, 'action' input is rendered separately.
        
        // Find the wrapper for the 'action' field (text input)
        // Since we are using 'fields' tuple in Admin, they might be in the same row or different rows
        // Django Admin usually puts each field in a div.form-row.field-FIELDNAME
        
        // We need to find .field-action
        // Search globally in the form context if ID matching is hard
        const form = selectElement.closest('form');
        const actionRow = form ? form.querySelector('.field-action') : null;
        const transferRow = form ? form.querySelector('.field-transfer_target') : null;
        
        // 1. Handle Action Text Input Visibility
        if (actionRow) {
            if (selectedValue === '其他') {
                actionRow.style.display = ''; // Show
                if (actionRow.style.display === 'none') actionRow.style.display = 'block';
                // Focus on input
                const input = actionRow.querySelector('input');
                if (input) {
                    input.value = ''; // Clear it for fresh input? Or keep previous?
                    // input.focus(); 
                }
            } else if (selectedValue === '') {
                 // Empty selection
                 actionRow.style.display = 'none';
            } else {
                // Predefined action selected
                actionRow.style.display = 'none';
                
                // Auto-fill the hidden/hidden-ish text input with the selected value
                // so that it passes validation if we were using just one field, 
                // but here we handle it in clean(), so we just need to ensure UI is clean.
                // However, our clean() logic relies on action_input being empty to know we rely on select?
                // No, clean logic says: if select is not 'Other', use select.
                // So we don't strictly need to fill the text input.
                
                // Optional: Clear text input to avoid confusion
                const input = actionRow.querySelector('input');
                if (input) input.value = selectedValue; 
            }
        }
        
        // 2. Handle Transfer Target Visibility
        if (transferRow) {
            if (selectedValue === '商机移交') {
                transferRow.style.display = ''; 
                if (transferRow.style.display === 'none') transferRow.style.display = 'block';
            } else {
                transferRow.style.display = 'none';
            }
        }
    }

    // Attach listeners
    const selects = document.querySelectorAll('.action-select');
    selects.forEach(select => {
        // Initial state
        toggleActionFields(select);
        
        select.addEventListener('change', function() {
            toggleActionFields(this);
        });
    });
    
    // Also need to handle initial load state if "Other" was selected (handled by python __init__ but JS needs to show/hide)
    
    // Expose global
    window.toggleActionFields = toggleActionFields;
});
