import frappe
from frappe import _
import csv
import re
from datetime import datetime
from frappe.model.naming import make_autoname

@frappe.whitelist()
def lead():
	lead_list=[]
	contact_list=[]
	with open('/home/deepak/Desktop/kisanmitra (copy).csv') as kmdata:
   		reader = csv.DictReader(kmdata)
   		for row in reader:
			lead_list.append(row.get("Contacts First Name")+" "+row.get("Contacts Last Name"))
			dict={"first_name":row.get("Contacts First Name"),
				  "last_name":row.get("Contacts Last Name"),
				  "mobile":row.get("Contacts Mobile Phone"),
				  "source":row.get("Contacts Contact Type"),
				  "creation":row.get("Contacts Created Time"),
				  "modified":row.get("Contacts Modified Time"),
				  "modified_by":row.get("Contacts Last Modified By")}
			contact_list.append(dict)

	unique_lead = list(set(lead_list))
	for i in unique_lead:
		
		contact_details = [j for j in contact_list if i == (j.get("first_name")+" "+j.get("last_name"))][0]
		modified_by_name = contact_details.get("modified_by")
		name = str(make_autoname('LEAD-','#####'))
		source = contact_details.get("source")
		creation = frappe.utils.get_datetime_str(datetime.strptime(contact_details.get("creation"), "%d-%m-%Y %I:%M %p"))
		modified = frappe.utils.get_datetime_str(datetime.strptime(contact_details.get("modified"), "%d-%m-%Y %I:%M %p"))
		if modified_by_name == "Visheshwar Rao":
			modified_by_name = "Vishesh rao Urvetha"
		modified_by = (frappe.get_all("User" , filters = {"full_name":modified_by_name})[0]).get("name")
		
		frappe.db.sql("""insert into `tabLead`
		(organization_lead,lead_name,company_name, name, source, creation, modified, owner,
		modified_by) values
		(1,%s,%s,%s,%s,%s,%s,%s,%s)""",(i,i,name,source,creation,modified,modified_by, modified_by))

		new_contact = frappe.new_doc("Contact")
		new_contact.first_name = contact_details.get("first_name")
		new_contact.last_name = contact_details.get("last_name")
		new_contact.mobile_no = contact_details.get("mobile")
		new_contact.append("links",{
			"link_doctype":"Lead",
			"link_name":name
			})
		new_contact.save()
	frappe.db.commit() 

@frappe.whitelist()
def issue():
	issue_list=[]
	with open('/home/deepak/Desktop/KMissue.csv') as kmdata:
   		reader = csv.DictReader(kmdata)
   		for row in reader:
			dict={"subject":row.get("Case Title"),
				  "description":row.get("Summary"),
				  "creation":row.get("Created Date"),
				  "name":row.get("Case Number"),
				  "modified":row.get("Modified Time"),
				  "owner":row.get("Created By"),
				  "resolution_details":row.get("Resolution"),
				  "modified_by":row.get("Last Modified By"),
				  "km_resolution_type":row.get("Resolution Type"),
				  "km_caller_name":row.get("Caller Name"),
				  "km_are_you_calling_for_yourself":row.get("Are you calling for yourself"),
				  "km_caller_relationship_with_farmer":row.get("Caller relationship with Farmer"),
				  "km_mandal_case":row.get("Mandal case"),
				  "km_village_case":row.get("Village Case"),
				  "km_caste_category":row.get("Caste Category"),
				  "km_caste":row.get("Caste"),
				  "recording_url":row.get("Phone Calls Recording"),
				  "sid":row.get("Phone Calls Source UUID"),
				  "km_other_caste":row.get("Other Caste"),
				  "km_case_category":row.get("Case Category"),
				  "farmer_name":row.get("Farmer Name"),
				  "km_state_case":"Telangana",
				  # "km_state_case":row.get("State Case"),
				  "km_district_case":row.get("District case"),
				  "km_relation":row.get("Relation"),
				  "km_relation_name":row.get("Relation Name"),
				  "km_call_type":row.get("Call Type") ,
				  "km_priority":row.get("Priority")}
			issue_list.append(dict)	
	for i in issue_list:
		
		name_prifix = 'VKB-' if str(i.get("name"))[0]=='V' or str(i.get("name"))[0]=='v' else 'KM-'
		name_suffix = str(map(int,re.findall('\d+', str(i.get("name"))))[0])
		while len(name_suffix) < 5:
			name_suffix = '0' + name_suffix
		name =str(str(name_prifix) + name_suffix)
		creation = frappe.utils.get_datetime_str(datetime.strptime(i.get("creation"), "%d-%m-%Y %I:%M %p"))
		modified = frappe.utils.get_datetime_str(datetime.strptime(i.get("modified"), "%d-%m-%Y %I:%M %p"))
		modified_by_name = i.get("modified_by")
		if modified_by_name == "Visheshwar Rao":
			modified_by_name = "Vishesh rao Urvetha"
		modified_by = (frappe.get_all("User" , filters = {"full_name":modified_by_name})[0]).get("name")
		km_are_you_calling_for_yourself = 1 if str(i.get("km_are_you_calling_for_yourself")) == 'yes' else 0
		lead = ''
		contact = ''
		if len((frappe.get_all("Lead", filters={"company_name":i.get("km_caller_name")}))):
			lead = (frappe.get_all("Lead", filters={"company_name":i.get("km_caller_name")}))[0].get("name")
		elif len((frappe.get_all("Lead", filters={"company_name":i.get("farmer_name")}))):
			lead = (frappe.get_all("Lead", filters={"company_name":i.get("farmer_name")}))[0].get("name")
		if lead:
			contact = frappe.db.get_value("Dynamic Link",{"link_name":lead},"parent")
		state = str(i.get("km_state_case"))
		district = str(i.get("km_district_case"))
 		mandal = str(i.get("km_mandal_case"))
 		village = str(i.get("km_mandal_case"))
					
		
		if not frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":"All Territories" ,"territory_name":state}) and \
		state:
			new_state_territory = frappe.new_doc("Territory")
			new_state_territory.is_group = 1
			new_state_territory.parent_territory = "All Territories"
			new_state_territory.territory_name = state
			new_state_territory.save()

		if not frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":state ,"territory_name":district}) and  \
		state and district:
			new_district_territory = frappe.new_doc("Territory")
			new_district_territory.is_group = 1
			new_district_territory.parent_territory = state
			new_district_territory.territory_name = district
			new_district_territory.save()

		if frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":district ,"territory_name":mandal}):
			mandal = mandal
		elif frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":district ,"territory_name":mandal + " (" + district + ")"}):
			mandal = mandal + " (" + district + ")"
		elif frappe.get_all("Territory",filters = {"territory_name":mandal}):
			mandal = mandal + " (" + district + ")"
		if not frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":district ,"territory_name":mandal}) and \
		district and mandal:
			new_mandal_territory = frappe.new_doc("Territory")
			new_mandal_territory.is_group = 1
			new_mandal_territory.parent_territory = district
			new_mandal_territory.territory_name = mandal
			new_mandal_territory.save()
 		

		if frappe.get_all("Territory",filters = {"parent_territory":mandal ,"territory_name":village}):
			village = village
		elif frappe.get_all("Territory",filters = {"parent_territory":mandal ,"territory_name":village + " (" + mandal + ")"}):
			village = village + " (" + mandal + ")"
		elif frappe.get_all("Territory",filters = {"territory_name":village}):
			village = village + " (" + mandal + ")"
		if not frappe.get_all("Territory",filters = {"parent_territory":mandal ,"territory_name":village}) and \
		mandal and village:
			new_village_territory = frappe.new_doc("Territory")
			new_village_territory.parent_territory = mandal
			new_village_territory.territory_name = village
			new_village_territory.save()			

		frappe.db.sql("""insert into `tabIssue`
		(subject, description, creation, name, modified, owner, resolution_details, modified_by,
		km_resolution_type, km_caller_name, km_are_you_calling_for_yourself, km_caller_relationship_with_farmer,
		km_mandal_case, km_village_case, km_caste_category, km_caste, contact, km_other_caste, km_case_category,
		km_district_case, km_relation, km_relation_name, raised_by, lead, sid, recording_url, communication_medium, 
		km_state_case, km_call_type, km_priority) values
		(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
		(i.get("subject"), i.get("description"), creation, name, modified,
		modified_by, i.get("resolution_details"), modified_by, i.get("km_resolution_type"),
		i.get("km_caller_name"), str(km_are_you_calling_for_yourself), i.get("km_caller_relationship_with_farmer"),
		mandal, village, i.get("km_caste_category"), i.get("km_caste"),
		contact, i.get("km_other_caste"), i.get("km_case_category"),district, i.get("km_relation"), 
		i.get("km_relation_name"), modified_by, lead, i.get("sid"), i.get("recording_url"), 'Phone', 
		state, i.get("km_call_type"), i.get("km_priority")))
	frappe.db.commit()		


@frappe.whitelist()
def comment():
	comment_list=[]
	with open('/home/deepak/Desktop/KMComments.csv') as kmdata:
   		reader = csv.DictReader(kmdata)
   		for row in reader:
   			dict={"case_number":row.get("Cases Case Number") ,
   				  "content":row.get("Comments Comment"),
   				  "reference_owner":row.get("Comments Creator"),
   				  "subject":row.get("Comments Related To"),
   				  "creation":row.get("Comments Created Time"),
   				  "modified":row.get("Comments Modified Time")}
			comment_list.append(dict)

	for i in comment_list:
		reference_name=''
		reference_doctype = ''
		status = 'Open'
		if i.get("case_number"):
			name_prifix = 'VKB-' if str(i.get("case_number"))[0]=='V' or str(i.get("case_number"))[0]=='v' else 'KM-'
			name_suffix = str(map(int,re.findall('\d+', str(i.get("case_number"))))[0])
			while len(name_suffix) < 5:
				name_suffix = '0' + name_suffix
			reference_name =str(str(name_prifix) + name_suffix)
			reference_doctype = "Issue"
			status = "Linked"
		name = frappe.generate_hash(length=10)
		creation = frappe.utils.get_datetime_str(datetime.strptime(i.get("creation"), "%d-%m-%Y %I:%M %p"))
		modified = frappe.utils.get_datetime_str(datetime.strptime(i.get("modified"), "%d-%m-%Y %I:%M %p"))
		modified_by_name = i.get("reference_owner")
		if modified_by_name == "Visheshwar Rao":
			modified_by_name = "Vishesh rao Urvetha"
		modified_by = (frappe.get_all("User" , filters = {"full_name":modified_by_name})[0]).get("name")
		sender_full_name = modified_by_name

		frappe.db.sql("""insert into `tabCommunication`
		(comment_type, communication_type, content, reference_owner, subject, 
		reference_doctype, reference_name, communication_date, user, 
		creation, modified, modified_by, name , status, 
		sender_full_name ,sent_or_received) values
		('Comment','Comment',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
		(i.get("content"),modified_by, i.get("subject"), reference_doctype, reference_name, creation,
		modified_by, creation, modified, modified_by, name ,status, sender_full_name, 'Send'))
	frappe.db.commit()		



@frappe.whitelist()
def phone_call():
	phone_call_list=[]
	with open('/home/deepak/Desktop/KMPhone_call.csv') as kmdata:
   		reader = csv.DictReader(kmdata)
   		for row in reader:
   			dict={"case_number":row.get("Cases Case Number") ,
   				  "reference_owner":row.get("Phone Calls Created By"),
   				  "subject":row.get("Phone Calls Cases"),
   				  "creation":row.get("Phone Calls Created Time"),
   				  "modified":row.get("Phone Calls Modified Time"),
   				  "modified_by":row.get("Phone Calls Last Modified By"),
   				  "sent_or_received":row.get("Phone Calls Direction"),
   				  "km_call_status":row.get("Phone Calls Call Status"),
   				  "km_call_customer":row.get("Phone Calls Customer"),
   				  "phone_no":row.get("Phone Calls Customer Number"),
   				  "km_calls_start_time":row.get("Phone Calls Start Time"),
   				  "km_calls_end_time":row.get("Phone Calls End Time"),
   				  "km_call_duration":row.get("Phone Calls Duration (sec)"),
   				  "km_call_gateway":row.get("Phone Calls Gateway")}
			phone_call_list.append(dict)

	for i in phone_call_list:
		if i.get("modified_by"):
			reference_name=''
			reference_doctype = ''
			km_calls_start_time = ''
			km_calls_end_time = ''
			status = 'Open'
			if i.get("case_number"):
				name_prifix = 'VKB-' if str(i.get("case_number"))[0]=='V' or str(i.get("case_number"))[0]=='v' else 'KM-'
				name_suffix = str(map(int,re.findall('\d+', str(i.get("case_number"))))[0])
				while len(name_suffix) < 5:
					name_suffix = '0' + name_suffix
				reference_name =str(str(name_prifix) + name_suffix)
				reference_doctype = "Issue"
				status = "Linked"
			name = frappe.generate_hash(length=10)
			creation = frappe.utils.get_datetime_str(datetime.strptime(i.get("creation"), "%d-%m-%Y %I:%M %p"))
			modified = frappe.utils.get_datetime_str(datetime.strptime(i.get("modified"), "%d-%m-%Y %I:%M %p"))
			if i.get("km_calls_start_time"):
				km_calls_start_time = frappe.utils.get_datetime_str(datetime.strptime(i.get("km_calls_start_time"), "%d-%m-%Y %I:%M %p"))
			if i.get("km_calls_end_time"):
				km_calls_end_time = frappe.utils.get_datetime_str(datetime.strptime(i.get("km_calls_end_time"), "%d-%m-%Y %I:%M %p"))
			modified_by_name = i.get("reference_owner")
			if modified_by_name == "Visheshwar Rao":
				modified_by_name = "Vishesh rao Urvetha"
			modified_by = (frappe.get_all("User" , filters = {"full_name":modified_by_name})[0]).get("name")
			sender_full_name = modified_by_name
			if i.get("sent_or_received") == "inbound":
				sent_or_received = "Received"
			else :
				sent_or_received = "Send"	

			frappe.db.sql("""insert into `tabCommunication`
			(comment_type, communication_type, reference_owner, subject, reference_doctype, reference_name, 
			communication_date, user, creation, modified, modified_by, name , status, sender_full_name , sent_or_received , 
			km_call_status , km_call_customer , phone_no , km_calls_start_time , km_calls_end_time , km_call_duration , 
			km_call_gateway ,owner) values 
			('Info', 'Communication', %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
			(modified_by ,i.get("subject") ,reference_doctype ,reference_name ,creation ,modified_by, creation, modified, 
			modified_by, name ,status ,sender_full_name ,sent_or_received ,i.get("km_call_status") ,i.get("km_call_customer") ,
			i.get("phone_no") ,km_calls_start_time ,km_calls_end_time ,i.get("km_call_duration") ,
			'Exotel' ,modified_by))

			if row.get("Phone Calls Customer Number"):
				if not len((frappe.get_all("Contact", filters={"mobile_no":row.get("Phone Calls Customer Number")}))):
					if m.km_caller_name == i.get("km_call_customer"):
						first_name = i.get("km_call_customer")
					elif i.get("km_call_customer"):
						first_name = i.get("km_call_customer")
					elif m.km_caller_name:
						first_name = m.km_caller_name
					if first_name:
						new_contact = frappe.new_doc("Contact")
						new_contact.first_name = first_name
						new_contact.last_name = row.get("Phone Calls Customer Number")
						new_contact.mobile_no = row.get("Phone Calls Customer Number")
						new_contact.save()
						m = frappe.get_doc("Issue",reference_name)
						if m.contact == '':
							m.contact = new_contact.name
							m.save()

	frappe.db.commit()	


@frappe.whitelist()
def vikarabad():
	vikarabad_list=[]
	vikarabad_village_list=[]
	duplicate_village_list = []
	with open('/home/deepak/Desktop/Vikarabad_Mapping.csv') as kmdata:
   		reader = csv.DictReader(kmdata)
   		for row in reader:
   			dict = {"mandal":row.get("mandal"),"Village":row.get("Village")}
   			vikarabad_village_list.append(row.get("Village"))
   			vikarabad_list.append(dict)	
   		unique_village_list = list(set(vikarabad_village_list))
   		for i in unique_village_list:
   			m = [ j for j in vikarabad_village_list if j == i]
   			if len(m) > 1:
   				duplicate_village_list.append(m[0])		
	for vkb in vikarabad_list:	
		mandal = str(vkb.get("mandal"))
		village = str(vkb.get("Village"))

		if [ k for k in duplicate_village_list if k == vkb.get("Village")]:
			village = village + " (" + mandal + ")"

		if mandal == "Vikarabad":
			mandal = "Vikarabad(M)"
		if village == "Vikarabad":
			village = "Vikarabad(V)"
		if frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":"Vikarabad" ,"territory_name":village}):
			village = village + " (" + mandal + ")"	

		if not frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":"Vikarabad" ,"territory_name":mandal}) and mandal:
			new_mandal_territory = frappe.new_doc("Territory")
			new_mandal_territory.is_group = 1
			new_mandal_territory.parent_territory = "Vikarabad"
			new_mandal_territory.territory_name = mandal
			new_mandal_territory.save()

		if not frappe.get_all("Territory",filters = {"parent_territory":mandal ,"territory_name":village}) and mandal and village:
			new_village_territory = frappe.new_doc("Territory")
			new_village_territory.parent_territory = mandal
			new_village_territory.territory_name = village
			new_village_territory.save()

	frappe.db.commit()					
   	return 	True


@frappe.whitelist()
def adilabad():
	adilabad_list=[]
	adilabad_village_list=[]
	duplicate_village_list = []

	with open('/home/deepak/Desktop/Adilabad_Mapping.csv') as kmdata:
   		reader = csv.DictReader(kmdata)
   		for row in reader:
   			dict = {"Mandal":row.get("Mandal"),"Village":row.get("Village")}
   			adilabad_village_list.append(row.get("Village"))	
   			adilabad_list.append(dict)
   		unique_village_list = list(set(adilabad_village_list))
   		for i in unique_village_list:
   			m = [ j for j in adilabad_village_list if j == i]
   			if len(m) > 1:
   				duplicate_village_list.append(m[0])
	for albd in adilabad_list:	
		mandal = str(albd.get("Mandal"))
		village = str(albd.get("Village"))
		if [ k for k in duplicate_village_list if k == albd.get("Village")]:
			village = village + " (" + mandal + ")"
		if frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":"Adilabad" ,"territory_name":village}):
			village = village + " (" + mandal + ")"		

		if not frappe.get_all("Territory",filters = {"is_group":1 ,"parent_territory":"Adilabad" ,"territory_name":mandal}) and mandal:
			new_mandal_territory = frappe.new_doc("Territory")
			new_mandal_territory.is_group = 1
			new_mandal_territory.parent_territory = "Adilabad"
			new_mandal_territory.territory_name = mandal
			new_mandal_territory.save()

		if not frappe.get_all("Territory",filters = {"parent_territory":mandal ,"territory_name":village}) and mandal and village:
			new_village_territory = frappe.new_doc("Territory")
			new_village_territory.parent_territory = mandal
			new_village_territory.territory_name = village
			new_village_territory.save()
		
	frappe.db.commit()					
   	return 	True
