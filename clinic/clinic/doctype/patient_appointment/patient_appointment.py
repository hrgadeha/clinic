# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe.utils import getdate, cint
from frappe import _
import datetime
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_receivable_account,get_income_account


class PatientAppointment(Document):
	def on_update(self):
		today = datetime.date.today()
		appointment_date = getdate(self.appointment_date)

		# If appointment created for today set as open
		#if today == appointment_date:
		#	frappe.db.set_value("Patient Appointment", self.name, "status", "Sc")
		#	self.reload()

	#def after_insert(self):
	#	# Check fee validity exists
	#	appointment = self
	#	validity_exist = validity_exists(appointment.physician, appointment.patient)
	#	if validity_exist:
	#		fee_validity = frappe.get_doc("Fee Validity", validity_exist[0][0])

			# Check if the validity is valid
	#		appointment_date = getdate(appointment.appointment_date)
	#		if (fee_validity.valid_till >= appointment_date) and (fee_validity.visited < fee_validity.max_visit):
	#			visited = fee_validity.visited + 1
	#			frappe.db.set_value("Fee Validity", fee_validity.name, "visited", visited)
	#			if fee_validity.ref_invoice:
	#				frappe.db.set_value("Patient Appointment", appointment.name, "sales_invoice", fee_validity.ref_invoice)
	#			frappe.msgprint(_("{0} has fee validity till {1}").format(appointment.patient, fee_validity.valid_till))
	#	confirm_sms(self)

	def save(self, *args, **kwargs):
		# duration is the only changeable field in the document
		if not self.is_new():
			self.db_set('duration', cint(self.duration))
		else:
			super(PatientAppointment, self).save(*args, **kwargs)


def appointment_cancel(appointment_id):
	appointment = frappe.get_doc("Patient Appointment", appointment_id)

	# If invoice --> fee_validity update with -1 visit
	if appointment.sales_invoice:
		validity = frappe.db.exists({"doctype": "Fee Validity", "ref_invoice": appointment.sales_invoice})
		if validity:
			fee_validity = frappe.get_doc("Fee Validity", validity[0][0])
			visited = fee_validity.visited - 1
			frappe.db.set_value("Fee Validity", fee_validity.name, "visited", visited)
			if visited <= 0:
				frappe.msgprint(
					_("Appointment cancelled, Please review and cancel the invoice {0}".format(appointment.sales_invoice))
				)
			else:
				frappe.msgprint(_("Appointment cancelled"))


@frappe.whitelist()
def get_availability_data(date, physician):
	"""
	Get availability data of 'physician' on 'date'
	:param date: Date to check in schedule
	:param physician: Name of the physician
	:return: dict containing a list of available slots, list of appointments and time of appointments
	"""

	date = getdate(date)
	weekday = date.strftime("%A")

	available_slots = []
	physician_schedule_name = None
	physician_schedule = None
	time_per_appointment = None

	# get physicians schedule
	physician_schedule_name = frappe.db.get_value("Doctor", physician, "physician_schedule")
	if physician_schedule_name:
		physician_schedule = frappe.get_doc("Physician Schedule", physician_schedule_name)
		time_per_appointment = frappe.db.get_value("Doctor", physician, "time_per_appointment")
		#frappe.msgprint(json.dumps(time_per_appointment))
	else:
		frappe.throw(_("Dr {0} does not have a Physician Schedule. Add it in Physician master".format(physician)))

	#custome:inside below block i did change divide block (from_time to to_time and each divide time per appointment)

	if physician_schedule:
		for t in physician_schedule.time_slots:
			if weekday == t.day:
				from_time=t.from_time
				to_time=t.to_time
				while from_time<to_time:
					time={}
					time["from_time"]=from_time
					time["to_time"]=from_time+datetime.timedelta(minutes = int(time_per_appointment))
					available_slots.append(time)
					from_time=from_time+datetime.timedelta(minutes = int(time_per_appointment))

	# `time_per_appointment` should never be None since validation in `Patient` is supposed to prevent
	# that. However, it isn't impossible so we'll prepare for that.
	if not time_per_appointment:
		frappe.throw(_('"Time Per Appointment" hasn"t been set for Dr {0}. Add it in Physician master.').format(physician))

	# if physician not available return
	if not available_slots:
		# TODO: return available slots in nearby dates
		frappe.throw(_("Physician not available on {0}").format(weekday))

	# if physician on leave return

	# if holiday return
	# if is_holiday(weekday):

	# get appointments on that day for physician
	appointments = frappe.get_all(
		"Patient Appointment",
		filters={"physician": physician, "appointment_date": date},
		fields=["name", "appointment_time", "duration", "status"])

	return {
		"available_slots": available_slots,
		"appointments": appointments,
		"time_per_appointment": time_per_appointment
	}


@frappe.whitelist()
def update_status(appointment_id, status):
	frappe.db.set_value("Patient Appointment", appointment_id, "status", status)
	if status == "Cancelled":
		appointment_cancel(appointment_id)


@frappe.whitelist()
def set_open_appointments():
	today = getdate()
	frappe.db.sql(
		"update `tabPatient Appointment` set status='Open' where status = 'Scheduled'"
		" and appointment_date = %s", today)


@frappe.whitelist()
def set_pending_appointments():
	today = getdate()
	frappe.db.sql(
		"update `tabPatient Appointment` set status='Pending' where status in "
		"('Scheduled','Open') and appointment_date < %s", today)


def confirm_sms(doc):
	if frappe.db.get_value("Healthcare Settings", None, "app_con") == '1':
		message = frappe.db.get_value("Healthcare Settings", None, "app_con_msg")
		send_message(doc, message)


@frappe.whitelist()
def getItemForInvoice(appointment):
	consultant_data=frappe.get_all("Consultation",filters=[("Consultation","appointment","=",appointment),("Consultation","is_bill","!=",1)],fields=["name"])
	items=[]
	if len(consultant_data)>0:
		consult=frappe.get_doc("Consultation",consultant_data[0].name)
		line_item={}
		line_item["item_code"]=frappe.db.get_value("Healthcare Settings","Healthcare Settings","consultant_item")
		line_item["qty"]=1
		line_item["consultation"]=consultant_data[0].name
		op_consulting_charge = frappe.db.get_value("Doctor",consult.physician, "op_consulting_charge")
		cost_center = frappe.db.get_value("Doctor",consult.physician, "cost_center")
		if op_consulting_charge:
			line_item["rate"] = op_consulting_charge
		if cost_center:
			line_item["cost_center"]=cost_center
		items.append(line_item)

	treatment_data=frappe.get_all("Client Treatment",filters=[("Client Treatment","appointment","=",appointment),("Client Treatment","status","in",["Pending","Completed"]),("Client Treatment","is_bill","!=",1)],fields=["name"])
	if len(treatment_data)>0:
		for row in treatment_data:
			treatment=frappe.get_doc("Client Treatment",row.name)
			line_item={}
			line_item["item_code"]=treatment.treatment
			line_item["qty"]=treatment.qty
			line_item["treatment"]=row.name
			cost_center = frappe.db.get_value("Doctor",treatment.doctor, "cost_center")
			if cost_center:
				line_item["cost_center"]=cost_center

			items.append(line_item)
	return items




@frappe.whitelist()
def create_invoice(company, physician, patient, appointment_id, appointment_date):
	if not appointment_id:
		return False

	#item_obj=getItemArray(company,physician,patient,appointment_id,appointment_date)
	item_object=getItemForInvoice(appointment_id)
	if len(item_object)>0:
		sales_invoice=frappe.get_doc(dict(
			doctype="Sales Invoice",
			customer=patient,
			due_date=getdate(),
			appointment=appointment_id,
			items=item_object
		)).insert()
		return sales_invoice.name
	else:
		return False	

def getItems(item_obj):
	items=[]
	counter=0
	obj=json.loads(item_obj)
	while counter<len(obj):
		line_item={}
		if not obj[counter][:2]=='CT':
			consult_data=frappe.get_doc("Consultation",obj[counter])
			line_item["item_code"]=frappe.db.get_value("Healthcare Settings","Healthcare Settings","consultant_item")
			line_item["qty"]=1
			op_consulting_charge = frappe.db.get_value("Doctor",consult_data.physician, "op_consulting_charge")
			cost_center = frappe.db.get_value("Doctor",consult_data.physician, "cost_center")

			if op_consulting_charge:
				line_item["rate"] = op_consulting_charge
			if cost_center:
				line_item["cost_center"]=cost_center

			items.append(line_item)

		else:
			treatment_data=frappe.get_doc("Client Treatment",obj[counter])
			line_item["item_code"]=treatment_data.treatment
			line_item["qty"]=treatment_data.qty
			cost_center = frappe.db.get_value("Doctor",treatment_data.doctor, "cost_center")
			if cost_center:
				line_item["cost_center"]=cost_center

			items.append(line_item)
		counter=counter+1
	return items



	
		


			
			
	


'''@frappe.whitelist()
def invoiceItem(name):
	appointment_details=frappe.get_doc("Patient Appointment",name)
	items=getItemArray(appointment_details.company,appointment_details.physician,appointment_details.client,name,appointment_details.appointment_date)
	if len(items)>0:
		return items
	else:
		return False		



def getItemArray(company, physician, patient, appointment_id, appointment_date):
	consultation_details=frappe.get_all("Consultation",filters={"docstatus":1,"patient":patient,"appointment":appointment_id,"physician":physician},fields=["name"])
	items=[]
	if consultation_details:
		for treatment in consultation_details:
			consultation_data=frappe.get_doc("Consultation",treatment.name)
			if len(consultation_data.treatment)>0:
				item_json={}
				item_json["item_name"]="Consulting Charges"
				item_json["description"]="Consulting Charges:  " + physician
				item_json["qty"] = 1
				item_json["uom"] = "Nos"
				item_json["conversion_factor"] = 1
				item_json["income_account"] = get_income_account(physician, company)
				op_consulting_charge = frappe.db.get_value("Doctor", physician, "op_consulting_charge")
				if op_consulting_charge:
					item_json["rate"] = op_consulting_charge
					item_json["amount"] = op_consulting_charge
				items.append(item_json)
				for treat_item in consultation_data.treatment:
					item_json={}
					treatment_data=frappe.get_all("Client Treatment",filters={"consulatation":treat_item.parent,"consulatation_treatment":treat_item.name,"status":"Completed"},fields=["treatment","qty"])
					if len(treatment_data)>0:
						item_json["item_code"]=treatment_data[0].treatment
						item_json["qty"]=treatment_data[0].qty
						items.append(item_json)	
			else:
				item_json={}
				item_json["item_name"]="Consulting Charges"
				item_json["description"]="Consulting Charges:  " + physician
				item_json["qty"] = 1
				item_json["uom"] = "Nos"
				item_json["conversion_factor"] = 1
				item_json["income_account"] = get_income_account(physician, company)
				op_consulting_charge = frappe.db.get_value("Doctor", physician, "op_consulting_charge")
				if op_consulting_charge:
					item_json["rate"] = op_consulting_charge
					item_json["amount"] = op_consulting_charge
				items.append(item_json)

	return items


'''
def get_fee_validity(physician, patient, date):
	validity_exist = validity_exists(physician, patient)
	if validity_exist:
		fee_validity = frappe.get_doc("Fee Validity", validity_exist[0][0])
		fee_validity = update_fee_validity(fee_validity, date)
	else:
		fee_validity = create_fee_validity(physician, patient, date)
	return fee_validity


def validity_exists(physician, patient):
	return frappe.db.exists({
			"doctype": "Fee Validity",
			"physician": physician,
			"patient": patient})


def update_fee_validity(fee_validity, date):
	max_visit = frappe.db.get_value("Healthcare Settings", None, "max_visit")
	valid_days = frappe.db.get_value("Healthcare Settings", None, "valid_days")
	if not valid_days:
		valid_days = 1
	if not max_visit:
		max_visit = 1
	date = getdate(date)
	valid_till = date + datetime.timedelta(days=int(valid_days))
	fee_validity.max_visit = max_visit
	fee_validity.visited = 1
	fee_validity.valid_till = valid_till
	fee_validity.save(ignore_permissions=True)
	return fee_validity


def create_fee_validity(physician, patient, date):
	fee_validity = frappe.new_doc("Fee Validity")
	fee_validity.physician = physician
	fee_validity.patient = patient
	fee_validity = update_fee_validity(fee_validity, date)
	return fee_validity


def create_invoice_items(appointment_id, physician, company, invoice):
	item_line = invoice.append("items")
	item_line.item_name = "Consulting Charges"
	item_line.description = "Consulting Charges:  " + physician
	item_line.qty = 1
	item_line.uom = "Nos"
	item_line.conversion_factor = 1
	item_line.income_account = get_income_account(physician, company)
	op_consulting_charge = frappe.db.get_value("Doctor", physician, "op_consulting_charge")
	if op_consulting_charge:
		item_line.rate = op_consulting_charge
		item_line.amount = op_consulting_charge
	return invoice

def create_invoice_items1(appointment_id, physician, company, invoice):
	item_line = invoice.append("items")
	item_line.item_name = "Consulting Charges"
	item_line.description = "Consulting Charges:  " + physician
	item_line.qty = 1
	item_line.uom = "Nos"
	item_line.conversion_factor = 1
	item_line.income_account = get_income_account(physician, company)
	op_consulting_charge = frappe.db.get_value("Doctor", physician, "op_consulting_charge")
	if op_consulting_charge:
		item_line.rate = op_consulting_charge
		item_line.amount = op_consulting_charge
	return invoice


@frappe.whitelist()
def create_consultation(appointment):
	appointment = frappe.get_doc("Patient Appointment", appointment)
	consultation = frappe.new_doc("Consultation")
	consultation.appointment = appointment.name
	consultation.patient = appointment.client
	consultation.patient_name=appointment.patient_name
	consultation.physician = appointment.physician
	consultation.doctor_name=appointment.doctor_name	
	consultation.consultation_date = appointment.appointment_date
	if appointment.sales_invoice:
		consultation.invoice = appointment.sales_invoice
	return consultation.as_dict()


def remind_appointment():
	if frappe.db.get_value("Healthcare Settings", None, "app_rem") == '1':
		rem_before = datetime.datetime.strptime(frappe.get_value("Healthcare Settings", None, "rem_before"), "%H:%M:%S")
		rem_dt = datetime.datetime.now() + datetime.timedelta(
			hours=rem_before.hour, minutes=rem_before.minute, seconds=rem_before.second)

		appointment_list = frappe.db.sql(
			"select name from `tabPatient Appointment` where start_dt between %s and %s and reminded = 0 ",
			(datetime.datetime.now(), rem_dt)
		)

		for i in range(0, len(appointment_list)):
			doc = frappe.get_doc("Patient Appointment", appointment_list[i][0])
			message = frappe.db.get_value("Healthcare Settings", None, "app_rem_msg")
			send_message(doc, message)
			frappe.db.set_value("Patient Appointment", doc.name, "reminded",1)

'''
def send_message(doc, message):
	patient = frappe.get_doc("Patient", doc.patient)
	if patient.mobile:
		context = {"doc": doc, "alert": doc, "comments": None}
		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		# jinja to string convertion happens here
		message = frappe.render_template(message, context)
		number = [patient.mobile]
		send_sms(number, message)'''


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Patient Appointment", filters)
	data = frappe.db.sql("""select name, patient, physician, status,
		duration, timestamp(appointment_date, appointment_time) as
		'appointment_date' from `tabPatient Appointment` where
		(appointment_date between %(start)s and %(end)s)
		and docstatus < 2 {conditions}""".format(conditions=conditions),
		{"start": start, "end": end}, as_dict=True, update={"allDay": 0})
	for item in data:
		item.appointment_datetime = item.appointment_date + datetime.timedelta(minutes = item.duration)
	return data
