from __future__ import unicode_literals
import frappe
from frappe.utils import cint, get_gravatar,flt,format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day
from frappe import throw, msgprint, _
from frappe.utils.password import update_password as _update_password
from frappe.desk.notifications import clear_notifications
from frappe.utils.user import get_system_managers
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
import frappe.permissions
import frappe.share
import re
import string
import random
import json
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import collections
import math
import logging
from operator import itemgetter 
import traceback


#custom:This function use to decide what is appointment status

@frappe.whitelist()
def app_error_log(title,error):
	d = frappe.get_doc({
			"doctype": "Custom Error Log",
			"title":str("User:")+str(title+" "+"App Name:Clinic"),
			"error":traceback.format_exc()
		})
	d = d.insert(ignore_permissions=True)
	return d


@frappe.whitelist()
def generateResponse(_type,status=None,message=None,data=None,error=None):
	response= {}
	if _type=="S":
		if status:
			response["status"]=status
		else:
			response["status"]="200"
		response["message"]=message
		response["data"]=data
	else:
		error_log=app_error_log(frappe.session.user,str(error))
		if status:
			response["status"]=status
		else:
			response["status"]="500"
		if message:
			response["message"]=message
		else:
			response["message"]="Something Went Wrong"		
		response["message"]=message
		response["data"]=None
	return response


@frappe.whitelist()
def checkAvailability(self,method):
	try:
		checkAppointment=frappe.get_all("Patient Appointment",filters=[("Patient Appointment","status","in",["Billed","To Bill","Under Treatment","Scheduled"]),("Patient Appointment","appointment_date","=",self.appointment_date),("Patient Appointment","physician","=",self.physician),("Patient Appointment","appointment_time","=",self.appointment_time)],fields=["name"])
		checkApp=frappe.db.sql("""select name from `tabPatient Appointment` where status="Schedule" and appointment_date=%s and physician=%s and appointment_time=%s""",(self.appointment_date,self.physician,self.appointment_time))	
		
	
		#frappe.msgprint(json.dumps(checkAppointment))
		if len(checkAppointment)>1:
			frappe.db.set_value("Patient Appointment", self.name, "status", "Waiting")
			return self.name
		else:
			frappe.db.set_value("Patient Appointment", self.name, "status", "Scheduled")
			return self.name

	except Exception as e:
		return generateResponse("F",error=e)

@frappe.whitelist()
def changeStatus(self,method):
	try:
		for item in self.items:
			if item.consultation:
				frappe.db.set_value("Consultation",item.consultation,"is_bill",1)
			if item.treatment:
				frappe.db.set_value("Client Treatment",item.treatment,"is_bill",1)
		if self.appointment:
			consultant_data=frappe.get_all("Consultation",filters=[("Consultation","appointment","=",self.appointment),("Consultation","is_bill","!=",1)],fields=["name"])
			treatment_data=frappe.get_all("Client Treatment",filters=[("Client Treatment","appointment","=",self.appointment),("Client Treatment","status","in",["Pending","Completed"]),("Client Treatment","is_bill","!=",1)],fields=["name"])
			if len(consultant_data)==0 and len(treatment_data)==0:
				frappe.db.set_value("Patient Appointment",self.appointment, "status", "Billed")
			else:
				frappe.db.set_value("Patient Appointment",self.appointment, "status", "Partial Billed")



	except Exception as e:
		return generateResponse("F",error=e)


@frappe.whitelist()
def updateDocument(self,method):
	try:
		if self.appointment:
			frappe.db.set_value("Patient Appointment",self.appointment,"status","Closed")
			treatment_data=frappe.get_all("Client Treatment",filters={'consulatation':self.name},fields=["name"])
			if len(treatment_data)>0:
				for treatment in treatment_data:
					tr_doc=frappe.get_doc("Client Treatment",treatment.name)
					if tr_doc.docstatus==0:
						tr_doc.submit()
						tr_doc_update=frappe.get_doc("Client Treatment",treatment.name)
						tr_doc_update.cancel()
					else:
						tr_doc.cancel()
	except Exception as e:
		return generateResponse("F",error=e)





'''
@frappe.whitelist()
def makeInvoice(appointment):
	try:
		appointment_data=frappe.get_doc("Patient Appointment",appointment)
		items=[]
		item_line={}
		item_line["item_code"]="BP"
		item_line["qty"]=1
		items.append(item_line)
		sales_invoice=frappe.get_doc(dict(
			customer=appointment_data.client,
			due_data=today(),
			appointment=appointment,
			items=items
		)).insert()
		return sales_invoice.name
	except Exception as e:
		return generateResponse("F",error=e)'''


#Not Useful

@frappe.whitelist()
def getItemForInvoice1(appointment):
	try:
		consultant_data=frappe.get_all("Consultation",filters=[("Consultation","appointment","=",appointment),("Consultation","is_bill","!=",1)],fields=["name"])
		items=[]
		if len(consultant_data)>0:
			consult=frappe.get_doc("Consultation",consultant_data[0].name)
			line_item={}
			line_item["item_code"]=frappe.db.get_value("Healthcare Settings","Healthcare Settings","consultant_item")
			line_item["doctor"]=consult.doctor_name
			line_item["date"]=consult.consultation_date
			line_item["name"]=consult.name
			items.append(line_item)

		treatment_data=frappe.get_all("Client Treatment",filters=[("Client Treatment","appointment","=",appointment),("Client Treatment","status","in",["Pending","Completed"]),("Client Treatment","is_bill","!=",1)],fields=["name"])
		if len(treatment_data)>0:
			for row in treatment_data:
				treatment=frappe.get_doc("Client Treatment",row.name)
				line_item={}
				line_item["item_code"]=treatment.treatment
				line_item["doctor"]=frappe.db.get_value("Doctor",treatment.medical_assitant,"first_name")
				line_item["date"]=treatment.date_time
				line_item["name"]=treatment.name
				items.append(line_item)
		return items

	except Exception as e:
		return generateResponse("F",error=e)


@frappe.whitelist()
def getItemForInvoice(appointment):
	try:
		data='<h4>Consultation and Treatments</h4><table class="table table-bordered" id="clinic"><tr><th>#</th><th>Item</th><th>Doctor</th><th>Date</th><th>Reference</th></tr>'
		consultant_data=frappe.get_all("Consultation",filters=[("Consultation","appointment","=",appointment),("Consultation","is_bill","!=",1)],fields=["name"])
		items=[]
		if len(consultant_data)>0:
			consult=frappe.get_doc("Consultation",consultant_data[0].name)
			data=data+"<tr><td><input type='checkbox'></td><td>"+str(frappe.db.get_value("Healthcare Settings","Healthcare Settings","consultant_item"))+"</td><td>"+str(consult.doctor_name)+"</td><td>"+str(consult.consultation_date)+"</td><td>"+str(consult.name)+"</td></tr>"

		treatment_data=frappe.get_all("Client Treatment",filters=[("Client Treatment","appointment","=",appointment),("Client Treatment","status","in",["Pending","Completed"]),("Client Treatment","is_bill","!=",1)],fields=["name"])
		if len(treatment_data)>0:
			for row in treatment_data:
				treatment=frappe.get_doc("Client Treatment",row.name)
				data=data+"<tr><td><input type='checkbox'></td><td>"+str(treatment.treatment)+"</td><td>"+str(frappe.db.get_value("Doctor",treatment.medical_assitant,"first_name"))+"</td><td>"+str(treatment.date_time)+"</td><td>"+str(treatment.name)+"</td></tr>"

		data=data+"</table>"
		return data	

	except Exception as e:
		return generateResponse("F",error=e)
