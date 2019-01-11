# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
		_("Client") + ":Link/Customer:100", _("Appointment")+ ":Link/Patient Appointment:120",
		_("Date") + ":Date:90", _("Doctor") + ":Link/Doctor:100",_("Doctor Name") + ":Link/Doctor:100",
		_("Clinic") + ":Link/Department:120", _("Treatment") + "::170", _("Medical Assistant") + ":Link/Doctor:120",
		_("Medical Assistant Name") + ":Link/Doctor:150", _("Status") + "::70", _("Cell No") + "::110", _("Email") + "::110"
	]

def get_data(filters):
	conditions = get_conditions(filters)
	data=[]
	appointment_data=frappe.db.sql("""select client,name,appointment_date,physician,doctor_name,clinic_name from `tabPatient Appointment` where docstatus=0 %s""" % conditions)
	if appointment_data:
		for appointment in appointment_data:
			row=[]
			row=[appointment[0],appointment[1],appointment[2],appointment[3],appointment[4],appointment[5]]
			treatment_data=frappe.db.sql("""select name,medical_assistant,medical_assistant_name,status from `tabClient Treatment` where appointment=%s""",appointment[1])
			for treatment in treatment_data:
				row.append(treatment[0])
				row.append(treatment[1])
				row.append(treatment[2])
				row.append(treatment[3])
			
			client_data=frappe.db.sql("""select cell_phone,email from `tabCustomer` where name=%s""",appointment[0])
			for client in client_data:
				row.append(client[0])
				row.append(client[1])
			data.append(row)
		return data
	else:
		return data	


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and appointment_date >= '%s'" % filters["from_date"]
	if filters.get("to_date"):
		conditions += " and appointment_date <= '%s'" % filters["to_date"]
	return conditions	


