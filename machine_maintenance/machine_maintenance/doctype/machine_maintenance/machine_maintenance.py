# Copyright (c) 2025, Mohammed Anas
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class MachineMaintenance(Document):

    def on_submit(self):
        self.create_journal_entry()

    @frappe.whitelist()
    def add_note(self, note):
        new_note = frappe.get_doc({
            "doctype": "CRM Note",
            "parent": self.name,
            "parenttype": self.doctype,
            "parentfield": "notes",
            "subject": frappe.utils.strip_html_tags(note)[:140] or "Note",
            "note": note,
            "added_by": frappe.session.user,
            "added_on": frappe.utils.now_datetime()
        })
        new_note.insert(ignore_permissions=True)
        return new_note

    @frappe.whitelist()
    def edit_note(self, note, row_id):
        child = frappe.get_doc("CRM Note", row_id)
        child.note = note
        child.subject = frappe.utils.strip_html_tags(note)[:140] or "Note"
        child.added_on = frappe.utils.now_datetime()
        child.save(ignore_permissions=True)
        return child

    @frappe.whitelist()
    def delete_note(self, row_id):
        child = frappe.get_doc("CRM Note", row_id)
        if child.parent != self.name:
            frappe.throw("Invalid Note")
        child.delete(ignore_permissions=True)
        return "ok"

    def validate(self):
        if self.status != "Completed" and self.machine_date:
            from frappe.utils import getdate, nowdate
            if getdate(self.machine_date) < getdate(nowdate()):
                self.status = "Overdue"

    @frappe.whitelist()
    def mark_completed(self):
        if self.docstatus == 1:
            frappe.throw(_("Cannot modify a submitted document."))

        if not self.completion_date:
            frappe.throw(_("Please set the Completion Date before marking as Completed."))

        self.status = "Completed"
        self.save(ignore_permissions=True)

        return {
            "status": self.status,
            "completion_date": self.completion_date
        }

    def create_journal_entry(self):
        if not self.technician:
            frappe.throw("Technician is required to create the Journal Entry.")

        
        company = frappe.db.get_single_value("Global Defaults", "default_company")
        if not company:
            frappe.throw("Please set Default Company in Global Defaults.")

        
        settings = frappe.get_single("Machine Maintenance Settings")
        debit_account = settings.debit_account
        credit_account = settings.credit_account

        if not debit_account or not credit_account:
            frappe.throw("Please set Debit and Credit Accounts in Machine Maintenance Settings.")

        
        amount = self.cost or 0
        if amount <= 0:
            frappe.throw("Cost must be greater than zero to create a Journal Entry.")

        
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = company
        je.posting_date = frappe.utils.nowdate()

        
        je.user_remark = self.name

        
        je.append("accounts", {
            "account": debit_account,
            "debit_in_account_currency": amount,
            "party_type": "Employee",
            "party": self.technician,
        })

        
        je.append("accounts", {
            "account": credit_account,
            "credit_in_account_currency": amount,
            "party_type": "Employee",
            "party": self.technician,
        })

        je.flags.ignore_permissions = True
        je.insert()
        je.submit()

        frappe.msgprint(f"Journal Entry <b>{je.name}</b> created.", alert=True)
    
    def before_save(self):
        self._prev_status = (
            frappe.db.get_value(self.doctype, self.name, "status")
            if self.name else None
        )

        if self.status != self._prev_status and self.status in ("Scheduled", "Completed", "Overdue"):
            frappe.enqueue(
                "machine_maintenance.machine_maintenance.email.machine_maintenance_email.send_status_email",
                queue="short",
                timeout=300,
                docname=self.name,
                from_status=self._prev_status,
                to_status=self.status
            )

