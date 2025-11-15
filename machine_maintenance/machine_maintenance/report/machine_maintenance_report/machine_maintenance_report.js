// Copyright (c) 2025, Mohammed Anas and contributors
// For license information, please see license.txt

frappe.query_reports["Machine Maintenance Report"] = {
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data || !data.row_color) return value;

        const colors = {
            red: "#ffcccc",
            yellow: "#fff6b3",
            green: "#ccffcc"
        };

        return `<span style="background:${colors[data.row_color]};
                              padding:4px; 
                              border-radius:4px;
                              display:block;">
                    ${value}
                </span>`;
    }
};
