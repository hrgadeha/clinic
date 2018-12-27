# -*- coding: utf-8 -*-
# Copyright (c) 2018, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.notifications import clear_doctype_notifications
from erpnext.controllers.selling_controller import SellingController

class ClientTreatment(Document):
	def on_submit(self):
		#frappe.msgprint("Submit")
		#self.update_status('Completed')
		frappe.db.set_value("Client Treatment",self.name,"status","Completed")
		if self.is_bill==0:
			consultation_name=frappe.get_all("Consultation",filters={"docstatus":1,"appointment":self.appointment},fields=["name"])
			if len(consultation_name)>0:
				treatment_data=frappe.get_all("Client Treatment",filters={"consulatation":consultation_name[0].name},fields=["name"])
				treatment_data_complete=frappe.get_all("Client Treatment",filters={"status":"Completed","consulatation":consultation_name[0].name},fields=["name"])
			
				if len(treatment_data)>0:
					if len(treatment_data)==len(treatment_data_complete):
						frappe.db.set_value("Patient Appointment",self.appointment,"status","To Bill")

	def update_status(self, status):
		self.set_status(update=True, status=status)
		clear_doctype_notifications(self)



					
