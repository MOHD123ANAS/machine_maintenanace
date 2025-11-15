import frappe

def send_status_email(docname, from_status=None, to_status=None):
    doc = frappe.get_doc("Machine Maintenance", docname)

    
    tech_email = frappe.db.get_value("Employee", doc.technician, "company_email") \
                 or frappe.db.get_value("Employee", doc.technician, "personal_email")

    if not tech_email:
        frappe.log_error(f"Technician {doc.technician} has no email", "Machine Maintenance Email")
        return

    
    if to_status == "Scheduled":
        status_msg = "scheduled"
    elif to_status == "Completed":
        status_msg = "completed"
    elif to_status == "Overdue":
        status_msg = "marked as overdue"
    else:
        status_msg = to_status

    subject = f"{doc.name} - Maintenance {to_status}"

    message = f"""
        <p>Hi {doc.technician},</p>

        <p>Hope this mail finds you well.</p>

        <p>The <b>{doc.machine_name}</b> item has been <b>{status_msg}</b>.</p>

        <p>Regards,<br>Maintenance System</p>
    """

    frappe.sendmail(
        recipients=[tech_email],
        subject=subject,
        message=message
    )
