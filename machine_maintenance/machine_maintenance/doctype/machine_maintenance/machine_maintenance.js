// Copyright (c) 2025, Mohammed Anas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machine Maintenance", {
    refresh(frm) {

        if (frm.doc.docstatus !== 1 && frm.fields_dict.notes_html) {

            frm.crm_notes = new erpnext.utils.CRMNotes({
                frm: frm,
                notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
            });

            frm.crm_notes.refresh();

            
            const oldHandler = frm.crm_notes.add_note;

            frm.crm_notes.add_note = function () {
                oldHandler.apply(this, arguments);

                setTimeout(() => {
                    frm.reload_doc().then(() => {
                        frm.crm_notes.refresh();
                    });
                }, 300);
            };
        }

        
        if (frm.doc.status !== "Completed" && frm.doc.docstatus === 0) {
            frm.add_custom_button("Mark Completed", function () {

                frm.call({
                    method: "mark_completed",
                    doc: frm.doc,
                    callback: function (r) {
                        frm.reload_doc();   
                    }
                });

            });
        }
    },


    
    onload(frm) {
        
        if (frm.is_new() || frm.doc.__islocal) {
            frm.set_value('machine_date', frappe.datetime.get_today());
        }
    },
    validate(frm) {
        frm.trigger("auto_update_status");
    },

    machine_date(frm) {
        frm.trigger("auto_update_status");
    },

    auto_update_status(frm) {
        if (frm.doc.status !== "Completed" &&
            frm.doc.machine_date &&
            frappe.datetime.str_to_obj(frm.doc.machine_date) < frappe.datetime.str_to_obj(frappe.datetime.get_today())) {

            frm.set_value("status", "Overdue");
        }
    }
});


frappe.ui.form.on("Machine Maintenance Parts", {
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

function calculate_amount(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);

    row.amount = (row.qty || 0) * (row.rate || 0);

    frm.refresh_field("parts_used");
    update_total_cost(frm);
}

function update_total_cost(frm) {
    let total = 0;

    (frm.doc.parts_used || []).forEach(row => {
        total += row.amount || 0;
    });

    frm.set_value("cost", total);
}
