## Machine Maintenance

### Installation

Make sure ERPNext and Frappe are installed as prerequisites.

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/MOHD123ANAS/machine_maintenanace
# Install the app on your site 
bench --site site-name install-app machine_maintenance
```

### How To setup Journal Entry
- Navigate to Machine Maintenance Settings and set the Credit Account (Company Currency).
- In the Machine Maintenance form, set the Debit Account in the currency being used while creating the Machine Maintenance document.
- If it is different from the company currency, enable the Is Multi-Currency checkbox.
- When the workflow is closed, the Journal Entry is automatically created.