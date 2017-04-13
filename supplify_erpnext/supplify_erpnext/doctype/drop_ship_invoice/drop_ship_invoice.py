# -*- coding: utf-8 -*-
# Copyright (c) 2015, Revant Nandgaonkar and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.utils import cint, flt, cstr
from frappe import _, msgprint, throw
from frappe.model.document import Document, get_doc
from frappe.model.mapper import get_mapped_doc
from supplify_erpnext.supplify_erpnext.doctype.drop_ship_settings.drop_ship_settings import get_drop_ship_settings
from erpnext.accounts.utils import get_account_currency
from erpnext.controllers.accounts_controller import set_balance_in_account_currency

class DropShipInvoice(Document):

	def validate(self):
		self.get_address()
		self.calculate_totals()
		self.validate_negative_inputs()
		self.base_grand_total = self.total

	def before_submit(self):
		if not self.sales_invoice: # add sales_invoice link field
			self.sales_invoice = self.make_sales_invoice()

		if not self.purchase_invoice: # add sales_invoice link field
			self.purchase_invoice = self.make_purchase_invoice()


	def on_cancel(self):
		from erpnext.accounts.general_ledger import delete_gl_entries
		delete_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

	def calculate_totals(self):
		total = 0.0
		purchase_total = 0.0
		sales_tax_total = 0.0
		purchase_tax_total = 0.0

		ds_settings = get_drop_ship_settings(self.company)
		for item in self.items:
			item.amount = flt(flt(item.rate) * flt(item.qty))
			if not item.purchase_rate:
				price_list_rate = frappe.db.get_value("Item Price",
				{
					"price_list": self.buying_price_list,
					"item_code": item.item_code

				}, "price_list_rate")
				if price_list_rate:
					item.purchase_rate = flt(price_list_rate)
				else:
					frappe.msgprint(_("Purchase Rate for Item {0} is not in Price List {1}".format(item.item_code, self.buying_price_list)))
			if item.purchase_rate > 0:
				item.purchase_amount = item.purchase_rate * item.qty
			else:
				frappe.throw(_("Enter Purchase Rate for Item {0}".format(item.item_code)))

			item.purchase_tax_amount = item.purchase_amount * flt(item.tax_rate / 100.0)
			item.sales_tax_amount = item.amount * flt(1 - (1/(1+(item.tax_rate/100.0)))) # Sales Rate includes tax
			item.selling_rate_excluding_tax = item.rate - (item.sales_tax_amount/item.qty) # Sales Rate excluding tax displayed
			total += flt(item.amount)
			purchase_total += flt(item.purchase_amount)
			sales_tax_total += flt(item.sales_tax_amount)
			purchase_tax_total += flt(item.purchase_tax_amount)

		self.total = total
		self.purchase_total = purchase_total
		self.sales_tax_total = sales_tax_total
		self.purchase_tax_total = purchase_tax_total

		self.total_commission = self.total - self.purchase_total
		self.commission_rate = (self.total_commission / self.total) * 100

	def make_gl(self, account_currency=None):
		from erpnext.accounts.general_ledger import make_gl_entries
		gl_map = []
		ds_settings = get_drop_ship_settings(self.company)

		ia = ds_settings["income_account"]
		ra = ds_settings["receivable_account"]
		pa = ds_settings["payable_account"]
		cc = ds_settings["cost_center"]
		gl_dict = frappe._dict({
			'company': self.company,
			'posting_date': self.posting_date,
			'voucher_type': self.doctype,
			'voucher_no': self.name,
			'remarks': self.get("remarks"),
			'fiscal_year': self.fiscal_year,
			'account': ia,
			'cost_center': cc,
			'debit': flt(0),
			'credit': flt(flt(self.total_commission) - flt(self.purchase_tax_total)), # if self.purchase_tax_total else flt(self.total_commission)
			'debit_in_account_currency': 0,
			'credit_in_account_currency': 0,
			'is_opening': "No" # or self.get("is_opening")
		})
		if not account_currency:
			account_currency = get_account_currency(gl_dict.account)
		set_balance_in_account_currency(gl_dict, account_currency, self.conversion_rate, self.company_currency)
		gl_map.append(gl_dict)

		gl_dict = frappe._dict({
			'company': self.company,
			'posting_date': self.posting_date,
			'voucher_type': self.doctype,
			'voucher_no': self.name,
			'remarks': self.get("remarks"),
			'fiscal_year': self.fiscal_year,
			'account': ra,
			'debit': flt(self.total),
			'credit': flt(0),
			'debit_in_account_currency': 0,
			'credit_in_account_currency': 0,
			'is_opening': "No", # or self.get("is_opening")
			'party_type': "Customer",
			'party': self.customer
		})
		if not account_currency:
			account_currency = get_account_currency(gl_dict.account)
		set_balance_in_account_currency(gl_dict, account_currency, self.conversion_rate, self.company_currency)
		gl_map.append(gl_dict)

		gl_dict = frappe._dict({
			'company': self.company,
			'posting_date': self.posting_date,
			'voucher_type': self.doctype,
			'voucher_no': self.name,
			'remarks': self.get("remarks"),
			'fiscal_year': self.fiscal_year,
			'account': pa,
			'debit': flt(0),
			'credit': flt(flt(self.purchase_total)  + flt(self.purchase_tax_total)), # if self.purchase_tax_total else flt(self.purchase_total),
			'debit_in_account_currency': 0,
			'credit_in_account_currency': 0,
			'is_opening': "No", # or self.get("is_opening")
			'party_type': "Supplier",
			'party': self.supplier
		})
		if not account_currency:
			account_currency = get_account_currency(gl_dict.account)

		set_balance_in_account_currency(gl_dict, account_currency, self.conversion_rate, self.company_currency)
		gl_map.append(gl_dict)

		if gl_map:
			make_gl_entries(gl_map, cancel=0, adv_adj=0)

	def validate_negative_inputs(self):
		for item in self.items:
			if item.qty <= 0:
				frappe.throw(_("Quantity cannot be zero or negative"))
			if item.rate <= 0:
				frappe.throw(_("Purchase Rate cannot be zero or negative"))
			if item.tax_rate <= 0:
				frappe.throw(_("Tax Rate cannot be zero or negative"))

	def get_address(self):
		from erpnext.accounts.party import get_party_details
		customer_details = get_party_details(self.customer, party_type="Customer")
		supplier_details = get_party_details(self.supplier, party_type="Supplier")
		self.address_display = customer_details["address_display"]
		self.supplier_address_display = supplier_details["address_display"]


	def make_sales_invoice(self):
		abbr = frappe.db.get_value("Company",frappe.defaults.get_defaults()["company"],"abbr")
		ds_settings = get_drop_ship_settings(self.company)

		ia = ds_settings["income_account"]

		defaults_temp = frappe.defaults.get_defaults()

		#Create a sales order if customer is selected.
		si = frappe.new_doc("Sales Invoice")
		si.transaction_date = self.posting_time

		si.company = defaults_temp.get("company")
		si.customer = self.customer


		si.currency = defaults_temp.get("currency")
		si.selling_price_list = defaults_temp.get("selling_price_list")

		for di_item in self.items:
			si.append("items", {
				"item_code": di_item.item_code,
				"qty": di_item.qty,
				"rate": di_item.rate - (di_item.purchase_rate + (di_item.purchase_tax_amount / di_item.qty)),
				"conversion_factor": 1.0,
				"amount": di_item.amount,
				"account":ia
			})
		si.append("taxes", {
			"charge_type": "Actual",
			"account_head": "Stock Received But Not Billed - " + abbr,
			"description": "Cost of Goods Sold",
			"tax_amount": self.purchase_total + self.purchase_tax_total
			})




		try:
			si.save()
			si.submit()
		except Exception, e:
			frappe.throw(_("Sales Invoice was not saved. <br/> %s" % (e)))
		else:
			return si.name


	def make_purchase_invoice(self):
		abbr = frappe.db.get_value("Company",frappe.defaults.get_defaults()["company"],"abbr")
		ds_settings = get_drop_ship_settings(self.company)
		defaults_temp = frappe.defaults.get_defaults()

		#Create a sales order if customer is selected.
		si = frappe.new_doc("Purchase Invoice")
		si.transaction_date = self.posting_time

		si.company = defaults_temp.get("company")
		si.supplier = self.supplier


		#si.rn_service_time_slot = self.starts_on + ", " + self.starts_on + " - " + self.ends_o

		si.currency = defaults_temp.get("currency")
		si.selling_price_list = defaults_temp.get("selling_price_list")

		for di_item in self.items:
			si.append("items", {
				"item_code": di_item.item_code,
				"qty": di_item.qty,
				"rate": di_item.purchase_rate,
				"conversion_factor": 1.0,
				"amount": di_item.purchase_amount
			})

		account_head = get_drop_ship_settings(frappe.defaults.get_defaults().company)['tax_account']
		si.append("taxes", {
			"charge_type": "Actual",
			"account_head": account_head,
			"description": frappe.db.get_value("Account", account_head, 'account_name'),
			"tax_amount": self.purchase_tax_total
			})


		try:
			si.save()
			si.submit()
		except Exception, e:
			frappe.throw(_("Purchase Invoice was not saved. <br/> %s" % (e)))
		else:
			return si.name

@frappe.whitelist()
def make_drop_ship_invoice(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Sales Invoice Advance
		#target.get_advances()

	def set_missing_values(source, target):
		target.is_pos = 0
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		# target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty

	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Drop Ship Invoice",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "Drop Ship Invoice Item",
			"field_map": {
				"name": "so_detail",
				"parent": "sales_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		},
		"Sales Taxes and Charges": {
			"doctype": "Sales Taxes and Charges",
			"add_if_empty": True
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist

# @frappe.whitelist()
# def make_supplier_payment_entry(supplier):
# 	pe_supplier = frappe.new_doc("Payment Entry")
# 	pe_supplier.posting_date = frappe.utils.datetime.datetime.today()
# 	pe_supplier.payment_type = "Pay"
# 	pe_supplier.party_type = "Supplier"
# 	pe_supplier.party = supplier
# 	pe_supplier.paid_to = get_drop_ship_settings(frappe.defaults.get_defaults().company)['payable_account']
# 	# supplier.paid_to =
# 	# pe_supplier.paid_from =
# 	# supplier.paid_amount =
# 	pe_supplier.save()
# 	frappe.db.commit()
# 	return pe_supplier.name


# @frappe.whitelist()
# def make_customer_payment_entry(customer):
# 	customer =  new_doc("Payment Entry")
# 	customer.payment_type = "Receive"
# 	customer.party_type = "Customer"
# 	customer.party = customer
# 	# customer.paid_to = frappe.db.get_value("Drop Ship Settings",filters={ "company": frappe.defaults.get_defaults().company}, fieldname="account")
# 	customer.paid_from = frappe.db.get_value("")

# 	frappe.db.commit()

@frappe.whitelist()
def get_account(company,party_type):
	if party_type == "Supplier":
		s = get_drop_ship_settings(company)['payable_account']
	else:
		s = get_drop_ship_settings(company)['receivable_account']
	return s


