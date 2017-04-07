// see license.txt
frappe.ui.form.on(cur_frm.doctype, {
refresh: function(doc) {
		cur_frm.add_custom_button(__('Sales Order'),
			function() {
			frappe.model.map_current_doc({
				method: "supplify_erpnext.supplify_erpnext.doctype.drop_ship_invoice.drop_ship_invoice.make_drop_ship_invoice",
				source_doctype: "Sales Order",
				get_query_filters: {
					docstatus: 1,
					status: ["not in", ["Stopped", "Closed"]],
					per_billed: ["<", 99.99],
					customer: cur_frm.doc.customer || undefined,
					company: cur_frm.doc.company
				}
			})
		}, __("Get items from"));


		cur_frm.add_custom_button(__('To Supplier'), function(){supplier_payment()},__("Make"));
		cur_frm.add_custom_button(__('Receive from customer'), function(){customer_payment()},__("Make"));
	}
});

function customer_payment() {

	frappe.call({
		method: "supplify_erpnext.supplify_erpnext.doctype.drop_ship_settings.drop_ship_settings.get_drop_ship_settings",
		args: {
			"company": cur_frm.doc.company
			},

		callback: function(r) {
		var pe = frappe.model.make_new_doc_and_get_name('Payment Entry');
		pe = locals['Payment Entry'][pe];
		pe.posting_date = frappe.datetime.get_today();
		pe.payment_type = "Receive";
		pe.party_type = "Customer";
		/*pe.party = cur_frm.doc.customer;*/
		pe.paid_from = r.message.receivable_account;
		frappe.route_options = {"customer": cur_frm.doc.customer}
		frappe._from_link = this
		frappe.set_route("Form", "Payment Entry", pe.name);
		},
	});
}

function supplier_payment() {

	frappe.call({
		method: "supplify_erpnext.supplify_erpnext.doctype.drop_ship_settings.drop_ship_settings.get_drop_ship_settings",
		args: {
			"company": cur_frm.doc.company
			},

		callback: function(r) {
			console.log(r.message.payable_account);
			var pe = frappe.model.make_new_doc_and_get_name('Payment Entry');
			pe = locals['Payment Entry'][pe];
			pe.posting_date = frappe.datetime.get_today();
			pe.payment_type = "Pay";
			pe.party_type = "Supplier";
			// pe.party = cur_frm.doc.supplier;
			pe.paid_to = r.message.payable_account;
			frappe.route_options = {"supplier": cur_frm.doc.supplier}
			frappe._from_link = this
			frappe.set_route("Form", "Payment Entry", pe.name);
		},
		});
}


cur_frm.add_fetch("item_code", "stock_uom", "stock_uom");
cur_frm.add_fetch("company", "default_currency", "company_currency");
cur_frm.add_fetch("customer", "customer_name", "customer_name");
cur_frm.add_fetch("supplier", "supplier_name", "supplier_name");

