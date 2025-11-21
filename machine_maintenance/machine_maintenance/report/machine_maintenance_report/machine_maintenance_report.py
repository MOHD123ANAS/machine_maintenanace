# Copyright (c) 2025, Mohammed Anas and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}

    consolidated = filters.get("consolidated")

    if consolidated:
        return get_consolidated_columns(), get_consolidated_data(filters)
    else:
        return get_detailed_columns(), get_detailed_data(filters)



def get_detailed_columns():
    return [
        {"label": "Machine", "fieldname": "machine_name", "fieldtype": "Link", "options": "Item", "width": 200},
        {"label": "Maintenance Date", "fieldname": "machine_date", "fieldtype": "Date", "width": 130},
        {"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Total Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 150},
        {"label": "row_color", "fieldname": "row_color", "fieldtype": "Data", "hidden": 1},
    ]




def get_consolidated_columns():
    return [
        {"label": "Machine", "fieldname": "machine_name", "fieldtype": "Link", "options": "Item", "width": 220},
        {"label": "Total Cost", "fieldname": "total_cost", "fieldtype": "Currency", "width": 150},
        {"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 120},
        {"label": "row_color", "fieldname": "row_color", "fieldtype": "Data", "hidden": 1},
    ]




def get_detailed_data(filters):
    conditions, values = build_conditions(filters)

    data = frappe.db.sql(
        f"""
        SELECT
            machine_name,
            machine_date,
            technician,
            status,
            cost
        FROM `tabMachine Maintenance`
        WHERE 1=1 {conditions}
        ORDER BY machine_date DESC
        """,
        values,
        as_dict=True
    )

    
    for d in data:
        if d.status == "Overdue":
            d.row_color = "red"
        elif d.status == "Scheduled":
            d.row_color = "yellow"
        elif d.status == "Completed":
            d.row_color = "green"
        else:
            d.row_color = ""

    return data



def get_consolidated_data(filters):
    conditions, values = build_conditions(filters)

    rows = frappe.db.sql(
        f"""
        SELECT
            machine_name,
            SUM(cost) AS total_cost,
            COUNT(name) AS count,
            -- Priority logic: Overdue > Scheduled > Completed
            MAX(
                CASE
                    WHEN status = 'Overdue' THEN 3
                    WHEN status = 'Scheduled' THEN 2
                    WHEN status = 'Completed' THEN 1
                    ELSE 0
                END
            ) AS priority_status
        FROM `tabMachine Maintenance`
        WHERE 1=1 {conditions}
        GROUP BY machine_name
        ORDER BY machine_name ASC
        """,
        values,
        as_dict=True
    )

    
    for r in rows:
        p = r.priority_status or 0

        if p == 3:
            r.row_color = "red"
        elif p == 2:
            r.row_color = "yellow"
        elif p == 1:
            r.row_color = "green"
        else:
            r.row_color = ""

        r.pop("priority_status", None)

    return rows



def build_conditions(filters):
    conditions = ""
    values = {}

    if filters.get("machine_name"):
        conditions += " AND machine_name = %(machine_name)s"
        values["machine_name"] = filters["machine_name"]

    if filters.get("technician"):
        conditions += " AND technician = %(technician)s"
        values["technician"] = filters["technician"]

    if filters.get("from_dates"):
        conditions += " AND machine_date >= %(from_dates)s"
        values["from_dates"] = filters["from_dates"]

    if filters.get("to_dates"):
        conditions += " AND machine_date <= %(to_dates)s"
        values["to_dates"] = filters["to_dates"]

    return conditions, values
