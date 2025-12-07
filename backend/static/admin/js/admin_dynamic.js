/* 
 * Custom Dynamic Behavior for Django Admin 
 * Handles auto-fill logic for Opportunity change form
 * Handles unsaved changes warning
 */

(function($) {
    $(document).ready(function() {
        // Only run on Opportunity change form
        if (!$('body').hasClass('model-opportunity') && !$('body').hasClass('change-form')) {
            return;
        }

        console.log('Admin Dynamic JS Loaded for Opportunity');

        // 1. Auto-fill Revenue from Signed Amount (Client-side Dynamic)
        var $signedAmount = $('#id_signed_amount');
        var $revenue = $('#id_revenue');

        if ($signedAmount.length && $revenue.length) {
            $signedAmount.on('input change', function() {
                var val = $(this).val();
                if (val) {
                    $revenue.val(val);
                }
            });
        }

        // 2. Auto-fill Team Member from Sales Manager
        var $salesManager = $('#id_sales_manager');
        
        if ($salesManager.length) {
            $salesManager.on('change', function() {
                var managerId = $(this).val();
                var managerName = $(this).find('option:selected').text();
                
                if (!managerId) return;

                var prefix = 'detailed_members'; 
                var $firstRowUser = $('#id_' + prefix + '-0-user');
                var $firstRowRole = $('#id_' + prefix + '-0-role');
                var $firstRowResp = $('#id_' + prefix + '-0-responsibility');

                if ($firstRowUser.length === 0) {
                    prefix = 'opportunityteammember_set';
                    $firstRowUser = $('#id_' + prefix + '-0-user');
                    $firstRowRole = $('#id_' + prefix + '-0-role');
                    $firstRowResp = $('#id_' + prefix + '-0-responsibility');
                }

                if ($firstRowUser.length) {
                    var currentVal = $firstRowUser.val();
                    if (!currentVal) {
                        $firstRowUser.val(managerId).trigger('change'); 
                        if ($firstRowRole.length) $firstRowRole.val('SALES_REP');
                        if ($firstRowResp.length) $firstRowResp.val('负责销售');
                    }
                }
            });
        }

        // 3. Unsaved Changes Warning
        var isDirty = false;
        var isSubmitting = false;

        // Detect changes on any input, select, or textarea
        $('form#opportunity_form :input').on('change input', function() {
            // Ignore internal hidden fields that might change automatically (like csrf)
            if ($(this).attr('name') === 'csrfmiddlewaretoken') return;
            isDirty = true;
        });

        // Allow submit without warning
        $('form#opportunity_form').on('submit', function() {
            isSubmitting = true;
        });

        // Hook into beforeunload
        $(window).on('beforeunload', function(e) {
            if (isDirty && !isSubmitting) {
                var message = '您有未保存的更改，确定要离开吗？';
                e.returnValue = message; // Standard for modern browsers
                return message;
            }
        });
    });
})(django.jQuery);
