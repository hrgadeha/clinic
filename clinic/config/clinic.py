from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Document"),
			"items": [
				{
					"type": "doctype",
					"name": "Doctor",
					"description": _("Doctor")
				},
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Client")
				},
				{
					"type": "doctype",
					"name": "Patient Appointment",
					"description": _("Client Appointment")
				},
				{
					"type": "doctype",
					"name": "Consultation",
					"description": _("Consultation")
				},
				{
					"type": "doctype",
					"name": "Client Treatment",
					"description": _("Client Treatment")
				}

			]
		},
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Doctor Designation",
					"description": _("Doctor Designation")
				},
				{
					"type": "doctype",
					"name": "Healthcare Settings",
					"description": _("Clinic Settings")
				},
				{
					"type": "doctype",
					"name": "Physician Schedule",
					"description": _("Doctor Schedule")
				}
			]



		},
		{
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Client Treatment History",
					"doctype": "Patient Appointment"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Treatment Analytics",
					"doctype": "Client Treatment"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Appointment Analytics",
					"doctype": "Patient Appointment"
				}

			]
		}
	]
