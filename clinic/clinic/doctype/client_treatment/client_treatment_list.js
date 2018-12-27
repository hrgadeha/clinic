/*
(c) ESS 2015-16
*/
frappe.listview_settings['Client Treatment'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {

		if(doc.status=="Pending"){
			return [__("Pending"), "darkgrey"];
		}
		if(doc.status=="Draft"){
			return [__("Pending"), "darkgrey"];
		}
		if(doc.docstatus==0){
			return [__("Pending"), "darkgrey"];
		}
		if(doc.status=="Completed"){
			return [__("Completed"), "purple"];
		}
		if(doc.is_bill){
			alert();

			return [__("Bill"), "green"];
		}



	},
};
