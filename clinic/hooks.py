# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "clinic"
app_title = "Clinic"
app_publisher = "GreyCube Technologies"
app_description = "Health Clinic Administration"
app_icon = "octicon octicon-star"
app_color = "pink"
app_email = "sales@greycube.in"
app_license = "MIT"

fixtures=["Custom Script"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/clinic/css/clinic.css"
# app_include_js = "/assets/clinic/js/clinic.js"

# include js, css files in header of web template
# web_include_css = "/assets/clinic/css/clinic.css"
# web_include_js = "/assets/clinic/js/clinic.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "clinic.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "clinic.install.before_install"
# after_install = "clinic.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "clinic.notifications.get_notification_config"

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
doc_events = {
	"Patient Appointment":{
		"after_insert":"clinic.api.checkAvailability"
	},
	"Consultation":{
		"after_submit":"clinic.api.makeTreatment",
		"on_cancel":"clinic.api.updateDocument"
	},
	"Sales Invoice":{
		"on_submit":"clinic.api.changeStatus"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"clinic.tasks.all"
# 	],
# 	"daily": [
# 		"clinic.tasks.daily"
# 	],
# 	"hourly": [
# 		"clinic.tasks.hourly"
# 	],
# 	"weekly": [
# 		"clinic.tasks.weekly"
# 	]
# 	"monthly": [
# 		"clinic.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "clinic.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "clinic.event.get_events"
# }

