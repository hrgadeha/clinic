/*
(c) ESS 2015-16
*/
frappe.listview_settings['Patient Appointment'] = {
	filters: [["status", "=", "Open"]],
	get_indicator: function(doc) {

		if(doc.status=="Waiting"){
			return [__("Waiting"), "darkgrey", "status,=,Waiting"];
		}
		if(doc.status=="Scheduled"){
			return [__("Scheduled"), "purple", "status,=,Scheduled"];
		}

		if(doc.status=="Closed"){
			return [__("Closed"), "blue", "status,=,Closed"];
		}

		if(doc.status=="Cancelled"){
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		}

		if(doc.status=="Under Treatment"){
			return [__("Under Treatment"), "yellow", "status,=,Under Treatment"];
		}
		if(doc.status=="To Bill"){
			return [__("To Bill"), "orange", "status,=,To Bill"];
		}
		if(doc.status=="Partial Billed"){
			return [__("Partial Billed"), "orange", "status,=,Partial Billed"];
		}
		if(doc.status=="Billed"){
			return [__("Billed"), "green", "status,=,Billed"];
		}



	},
};
