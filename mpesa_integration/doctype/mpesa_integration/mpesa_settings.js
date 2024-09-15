frappe.ui.form.on('Mpesa Settings', {
    refresh: function(frm) {
        frm.add_custom_button(__('Get Account Balance'), function() {
            frappe.call({
                method: 'mpesa_integration.mpesa_settings.mpesa_settings.get_account_balance',
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('Account Balance: {0}', [r.message]));
                    }
                }
            });
        });
    }
});
