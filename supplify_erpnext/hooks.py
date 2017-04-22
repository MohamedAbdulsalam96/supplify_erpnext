# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "supplify_erpnext"
app_title = "Supplify Erpnext"
app_publisher = "Revant Nandgaonkar"
app_description = "Drop Ship App for Supplify"
app_icon = "octicon octicon-package"
app_color = "#489126"
app_email = "support@castlecraft.in"
app_version = "1.0.0"
app_license = "GPL v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/supplify_erpnext/css/supplify_erpnext.css"
# app_include_js = "/assets/supplify_erpnext/js/supplify_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/supplify_erpnext/css/supplify_erpnext.css"
# web_include_js = "/assets/supplify_erpnext/js/supplify_erpnext.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "supplify_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "supplify_erpnext.install.before_install"
# after_install = "supplify_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "supplify_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"supplify_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"supplify_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"supplify_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"supplify_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"supplify_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "supplify_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "supplify_erpnext.event.get_events"
# }
fixtures = [{"dt":"Custom Script", "filters": [["name", "in", ["Payment Entry-Client"]]]}]