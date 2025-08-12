from flask import Flask, flash, redirect, render_template, request, url_for
import mysql.connector
from flask_cors import CORS
import calendar

app = Flask(__name__)
CORS(app)
app.secret_key = '123789456'

# Database config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'NHA@2004',
    'database': 'nha_db'
}

# home page route
@app.route('/')
def home():
    return render_template('home.html')

# Route to submission financial year 
@app.route('/financial_year_form', methods=['GET', 'POST'])
def financial_year_form():
    error = None
    success = None

    # If the request method is POST, it means the form was submitted
    if request.method == 'POST':
        # Get all submitted financial years as a list (e.g., ['2020-2021', '2021-2022'])
        financial_years = request.form.getlist('financialyear[]')

        try:
            # Connect to MySQL database using your config
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            count = 0  # to count how many records are successfully inserted

            # Loop through the submitted years
            for fy in financial_years:
                fy = fy.strip()  # remove any leading/trailing spaces
                if fy:  # only insert if not empty
                    cursor.execute(
                        "INSERT INTO financial_year (financial_year) VALUES (%s)", (fy,)
                    )
                    count += 1  # count inserted records

            conn.commit()  # save changes in DB

            # Flash a success message with the number of inserted years
            success = f"✅ {count} financial year(s) submitted successfully!"
            flash(success, 'success')

        except Exception as e:
            # If any error occurs, flash an error message
            error = f"❌ Error adding financial year: {e}"
            flash(error, 'danger')

        finally:
            # Close cursor and connection if they were opened
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Redirect to the same page after form submission (prevents resubmission on refresh)
        return redirect(url_for('financial_year_form'))

    # If method is GET, just render the form
    return render_template('financial_year_form.html', success=success, error=error)

# Route to show financial year list
@app.route('/financial_year_list', methods=['GET', 'POST'])
def financial_year_list():
    financialyear = request.args.get('financialyear')
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all financial years for dropdown from 'financial_year' table
        cursor.execute("SELECT financial_year FROM financial_year ORDER BY financial_year DESC")
        financial_years = cursor.fetchall()

        if financialyear:
            cursor.execute("SELECT * FROM financial_year WHERE financial_year LIKE %s", (financialyear,))
        else:
            cursor.execute("SELECT * FROM financial_year ORDER BY id DESC")
        records = cursor.fetchall()
        
    except Exception as e:
        records = []
        financial_years = []
        print("Error fetching records:", e)
    finally:
        cursor.close()
        conn.close()
    return render_template('financial_year_list.html', records=records, financialyear=financialyear, financial_years=financial_years)

# Route to delete a financial year record
@app.route('/delete_financial_year/<int:id>', methods=['POST'])
def delete_financial_year(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financial_year WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Financial year deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting financial year.", 'danger')
        print("Delete error:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('financial_year_list'))

# Form for budget submission
@app.route('/form', methods=['GET', 'POST'])
def form():
    error = None
    success = None
    financial_years = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT financial_year FROM financial_year ORDER BY financial_year DESC")
        financial_years = cursor.fetchall()
    except Exception as e:
        print("Error fetching financial years:", e)
        financial_years = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if request.method == 'POST':
        # Get form values
        financial_year = request.form.get('financialyear')
        totalbudget = request.form.get('totalbudget')
        budgetmonth = request.form.get('budgetmonth')
        budgetused = request.form.get('budgetused')
        budgetupto = request.form.get('budgetupto')

        # Validate numeric input
        try:
            totalbudget_val = float(totalbudget)
            budgetused_val = float(budgetused)
            budgetupto_val = float(budgetupto)
        except ValueError:
            error = "⚠️ Invalid numeric values."
            return render_template('form.html', financial_years=financial_years, error=error)

        # Validate month format
        try:
            year, month = map(int, budgetmonth.split('-'))
            reporting_month_last_day = calendar.monthrange(year, month)[1]
        except:
            error = "⚠️ Invalid month format. Use YYYY-MM."
            return render_template('form.html', financial_years=financial_years, error=error)

        # Calculate remaining budget
        remaining_budget = totalbudget_val - budgetupto_val

        # Insert data into DB
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO budget (
                    financial_year,
                    total_budget,
                    budget_month,
                    budget_used,
                    budget_used_upto_june,
                    reporting_month_last_day,
                    remaining_budget
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                financial_year,
                totalbudget_val,
                budgetmonth,
                budgetused_val,
                budgetupto_val,
                reporting_month_last_day,
                remaining_budget
            ))
            conn.commit()
            success = "✅ Budget data submitted successfully!"
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template('form.html', financial_years=financial_years, success=success, error=error)

    return render_template('form.html', financial_years=financial_years)

# Route to show budget list
@app.route('/budget_list')
def show_budget_list():
    selected_year = request.args.get('financialyear')
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all financial years for dropdown from 'financial_year' table
        cursor.execute("SELECT financial_year FROM financial_year ORDER BY financial_year DESC")
        financial_years = cursor.fetchall()  # this gives list of dicts with 'financial_year'

        # Fetch budget records filtered by selected financial year
        if selected_year:
            cursor.execute("SELECT * FROM budget WHERE financial_year = %s ORDER BY id DESC", (selected_year,))
        else:
            cursor.execute("SELECT * FROM budget ORDER BY id DESC")

        records = cursor.fetchall()

    except Exception as e:
        print("Error:", e)
        records = []
        financial_years = []

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'budget_list.html',
        records=records,
        financial_years=financial_years,
        selected_year=selected_year
    )

# Route to delete a budget record
@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budget WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Record deleted successfully.", 'success')
    except Exception as e:
        flash("Error deleting record.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('show_budget_list'))

# Route to edit a budget record
@app.route('/edit_form/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    if request.method == 'POST':
        financial_year = request.form['financialyear']
        total_budget = float(request.form['totalbudget'])
        budget_month = request.form['budgetmonth']
        budget_used = float(request.form['budgetused'])
        budget_upto = float(request.form['budgetupto'])
        reporting_day = request.form['reporting_month_last_day']

        # ✅ Calculate remaining budget here
        remaining = total_budget - budget_upto

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE budget SET
                    financial_year = %s,
                    total_budget = %s,
                    budget_month = %s,
                    budget_used = %s,
                    budget_used_upto_june = %s,
                    reporting_month_last_day = %s,
                    remaining_budget = %s
                WHERE id = %s
            """, (
                financial_year, total_budget, budget_month,
                budget_used, budget_upto, reporting_day, remaining, id
            ))
            conn.commit()
            flash("✅ Record updated successfully.", 'success')
        except Exception as e:
            flash("Error updating record.", 'danger')
            print("Update error:", e)
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('show_budget_list'))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM budget WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("Error loading record.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_form.html', record=record)

# Route for head/item form submission
@app.route('/head_form', methods=['GET', 'POST'])
def head_form():
    error = None
    success = None

    if request.method == 'POST':
        item_names = request.form.getlist('itemname[]')
        quantity = request.form.get('quantity')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert all non-empty item names
            for item in item_names:
                item = item.strip()
                if item:
                    cursor.execute("INSERT INTO item (items_name, quantity) VALUES (%s, %s)", (item, quantity,))

            conn.commit()
            success = f"✅ {len([i for i in item_names if i.strip()])} items submitted successfully!"
        except Exception as e:
            error = f"❌ Failed to insert items: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('head_form.html', success=success, error=error)

# head/items List route
@app.route('/item_list', methods=['GET'])
def item_list():
    items_name = request.args.get('items_name', default='')
    
    records = []
    quantity = 0
    total_quantity = 0
    percentage_of_item = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, item_name FROM item")
        items = cursor.fetchall()
    except Exception as e:
        print("Error fetching items:", e)
        items = []

    if items_name:
        cursor.execute("SELECT * FROM item WHERE items_name LIKE %s", ('%' + items_name + '%',))
    else:
        cursor.execute("SELECT * FROM item")

    records = cursor.fetchall()

    if records:
        
        total_quantity = sum(int(r['quantity']) for r in records if r['quantity'])
        for r in records:
            quantity = int(r['quantity']) if r['quantity'] else 0
            r['percentage_of_item'] = round((quantity / total_quantity) * 100) if total_quantity > 0 else 0
    else:
        total_quantity = 0
        
    conn.close()

    return render_template("item_list.html", records=records, items_name=items_name, items=items, quantity=quantity, total_quantity=total_quantity, percentage_of_item=percentage_of_item)

# Route to delete an item
@app.route('/delete_item/<int:id>', methods=['POST'])
def delete_item(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM item WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Item deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('item_list'))

# Route to edit an item
@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    error = None
    success = None
    items = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, items_name, quantity FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('item_list.html', items=[], error=error, success=success)
    
    if request.method == 'POST':
        item_name = request.form['itemname']
        quantity = request.form['quantity']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE item SET 
                    items_name = %s,
                    quantity = %s
                WHERE id = %s 
            """,(
                item_name, quantity, id
            ))
            conn.commit()
            flash("✅ Item updated successfully.", 'success')
        except Exception as e:
            flash("❌ Error updating item.", 'danger')
            print("Update error:", e)
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('item_list'))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM item WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error loading item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_item.html', items=items, record=record)

# procurement form submission
@app.route('/procrument_form', methods=['GET', 'POST'])
def procrument_form():
    error = None
    success = None
    items = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('procrument_form.html', items=[], error=error, success=success)

    if request.method == 'POST':
        item = request.form.get('item')
        units = request.form.get('units')
        expenditure = request.form.get('expenditure')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO procurement (item_name, units, expenditure)
                VALUES (%s, %s, %s)
            """, (item, units, expenditure))
            conn.commit()
            success = "✅ Data saved successfully!"
        except Exception as e:
            error = f"❌ Error inserting data: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('procrument_form.html', items=items, error=error, success=success)

# Procurement item list route
@app.route('/procurement_item_list')
def procurement_item_list():
    item_name = request.args.get('item_name', default='')
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, item_name FROM item")
        items = cursor.fetchall()
    except Exception as e:
        print("Error fetching items:", e)
        items = []
    
    if item_name:
        cursor.execute("SELECT * FROM procurement WHERE item_name LIKE %s", ('%' + item_name + '%',))
    else:
        cursor.execute("SELECT * FROM procurement")
    
    records = cursor.fetchall()
    conn.close()

    return render_template('procurement_item_list.html', records=records, item_name=item_name, items=items)

# Route to delete a procrument item
@app.route('/delete_procrument/<int:id>', methods=['POST'])
def delete_procrument(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM procurement WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Procrument deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('procurement_item_list'))

# Route to edit a procurement item
@app.route('/edit_procrument/<int:id>', methods=['GET', 'POST'])
def edit_procrument(id):
    error = None
    success = None
    items = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('procurement_item_list.html', items=[], error=error, success=success)
    
    if request.method == 'POST':
        item_name = request.form['item_name']
        units = request.form['units']
        expenditure = request.form['expenditure']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE procurement 
                SET item_name = %s, units = %s, expenditure = %s 
                WHERE id = %s
            """, (item_name, units, expenditure, id))
            conn.commit()
            flash("✅ Procurement updated successfully.", 'success')
        except Exception as e:
            flash("❌ Error updating item.", 'danger')
            print("Update error:", e)
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('procurement_item_list'))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM procurement WHERE id = %s", (id,))
        record = cursor.fetchone()

        if record is None:
            flash("❌ Record not found!", 'danger')
            return redirect(url_for('procurement_item_list'))

    except Exception as e:
        flash("❌ Error loading item.", 'danger')
        print("Fetch error:", e)
        return redirect(url_for('procurement_item_list'))
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_procrument.html', items=items, record=record)

# Repair and Maintenance form submission
@app.route('/repair_maintenance', methods=['GET', 'POST'])
def repair_form():
    error = None
    success = None
    items = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('repair_maintenance.html', items=[], error=error, success=success)

    if request.method == 'POST':
        itemlist = request.form.get('itemlist')
        units = request.form.get('units')
        unit = request.form.get('unit')
        hoursspend = request.form.get('hoursspend')
        days = request.form.get('days')
        expenditure = request.form.get('expenditure')

        try:
            units = int(units)
            unit = int(unit)
            item_total = units + unit
            expenditure = float(expenditure)

            # Reconnect to DB to calculate total expenditure (include current)
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(expenditure) FROM repair_maintenance")
            result = cursor.fetchone()
            total_expenditure = float(result[0]) if result[0] else 0
            total_expenditure += expenditure  # Include the current one

            # Correct calculations
            percentage_of_an_item = round((expenditure / total_expenditure) * 100) if total_expenditure > 0 else 0
            avg_cost_per_unit = expenditure / unit if unit > 0 else 0
            total_unit_repaired_in_house = units
            total_unit_repaired_external = unit
        except ValueError:
            error = "⚠️ Invalid numeric values."
            return render_template('repair_maintenance.html', items=items, error=error, success=success)

        try:
            cursor.execute("""
                INSERT INTO repair_maintenance (
                    item_name, unit_in_house, units_externals, hours_spend_in_house, 
                    days_externals, expenditure, item_total, percentage_of_an_item, 
                    avg_cost_per_unit, total_unit_repaired_in_house, total_unit_repaired_external
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                itemlist, units, unit, hoursspend, days, expenditure, item_total,
                percentage_of_an_item, avg_cost_per_unit,
                total_unit_repaired_in_house, total_unit_repaired_external
            ))
            conn.commit()
            success = "✅ Repair & Maintenance data submitted successfully!"
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('repair_maintenance.html', items=items, error=error, success=success)

# Repair and Maintenance item list route
@app.route('/repair_maintenance_list')
def repair_maintenance_list():
    items_name = request.args.get('items_name', default='')

    records = []
    total_items = total_expenditure = unit_in_house = units_externals = 0
    hours_spend_in_house = days_externals = avg_cost_per_unit = percenteage_inhouse_unit = percenteage_external_unit = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, item_name FROM item")
        items = cursor.fetchall()
    except Exception as e:
        print("Error fetching items:", e)
        items = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # ✅ Filter by item_name if given
        if items_name:
            cursor.execute("SELECT * FROM repair_maintenance WHERE item_name LIKE %s", ('%' + items_name + '%',))
        else:
            cursor.execute("SELECT * FROM repair_maintenance")

        records = cursor.fetchall()

        if records:  # Avoid division by zero if no records
            total_items = sum(int(r['item_total']) for r in records if r['item_total'])
            total_expenditure = sum(int(r['expenditure']) for r in records if r['expenditure'])
            unit_in_house = sum(int(r['unit_in_house']) for r in records if r['unit_in_house'])
            units_externals = sum(int(r['units_externals']) for r in records if r['units_externals'])
            hours_spend_in_house = sum(int(r['hours_spend_in_house']) for r in records if r['hours_spend_in_house'])
            days_externals = sum(int(r['days_externals']) for r in records if r['days_externals'])

            avg_cost_per_unit = total_expenditure / units_externals if units_externals > 0 else 0
            percenteage_inhouse_unit = (unit_in_house / total_items * 100) if total_items > 0 else 0
            percenteage_external_unit = (units_externals / total_items * 100) if total_items > 0 else 0

            for r in records:
                expenditure = float(r['expenditure']) if r['expenditure'] else 0
                r['percentage_of_an_item'] = round((expenditure / total_expenditure) * 100) if total_expenditure > 0 else 0
        else:
            # Default values if no matching record
            avg_cost_per_unit = 0
            percenteage_inhouse_unit = 0
            percenteage_external_unit = 0

    except Exception as e:
        print("Error fetching repair and maintenance items:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return render_template(
        'repair_maintenance_list.html',
        records=records,
        total_items=total_items,
        total_expenditure=total_expenditure,
        unit_in_house=unit_in_house,
        units_externals=units_externals,
        percenteage_inhouse_unit=percenteage_inhouse_unit,
        percenteage_external_unit=percenteage_external_unit,
        hours_spend_in_house=hours_spend_in_house,
        days_externals=days_externals,
        avg_cost_per_unit=avg_cost_per_unit,
        items_name=items_name,
        items=items
    )

# Route to delete a repair maintenance item
@app.route('/delete_repair_maintenance/<int:id>', methods=['POST'])
def delete_repair_maintenance(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM repair_maintenance WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Repair maintenance deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('repair_maintenance_list'))

# Route to edit a repair maintenance item
@app.route('/edit_repair_maintenance/<int:id>', methods=['GET', 'POST'])
def edit__repair_maintenance(id):
    if request.method == 'POST':
        itemlist = request.form['itemlist']
        units = int(request.form['units'])
        hoursspend = request.form['hoursspend']
        unit = int(request.form['unit'])
        days = request.form['days']
        expenditure = request.form['expenditure']
        item_total = units + unit 

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE repair_maintenance SET
                    item_name = %s,
                    unit_in_house = %s,
                    units_externals = %s,
                    hours_spend_in_house = %s,
                    days_externals = %s,
                    expenditure = %s,
                    item_total = %s
                WHERE id = %s
            """, (itemlist, units, unit, hoursspend, days, expenditure, item_total, id))

            conn.commit()
            flash("✅ Repair & Maintenance updated successfully.", 'success')
        except Exception as e:
            flash("❌ Error updating item.", 'danger')
            print("Update error:", e)
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('repair_maintenance_list'))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM repair_maintenance WHERE id = %s", (id,))
        record = cursor.fetchone()

        if record is None:
            flash("❌ Record not found!", 'danger')
            return redirect(url_for('repair_maintenance_list'))

    except Exception as e:
        flash("❌ Error loading item.", 'danger')
        print("Fetch error:", e)
        return redirect(url_for('repair_maintenance_list'))
    finally:
        cursor.close()
        conn.close()

    # ✅ Ensure you always return a response
    return render_template('edit_repair_maintenance.html', record=record)

# Complaints form submission
@app.route('/complaints_form', methods=['GET', 'POST'])
def complaints_form():
    error = None
    success = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.close()
    except Exception as e:
        error = f"Not Found: {e}"
        return render_template('complaints_form.html', error=error, success=success)

    if request.method == 'POST':
        # Get form data
        network_resolved = request.form.get('network_resolved')
        network_pending = request.form.get('network_pending')
        it_resolved = request.form.get('it_resolved')
        it_pending = request.form.get('it_pending')
        hours_spend = request.form.get('hours_spend')

        try:
            network_resolved = int(network_resolved)
            network_pending = int(network_pending)
            total_calls_network = network_resolved + network_pending
            it_resolved = int(it_resolved)
            it_pending = int(it_pending)
            total_calls_it = it_resolved + it_pending
            grand_total_calls = total_calls_network + total_calls_it

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
        except ValueError:
            error = "⚠️ Invalid numeric values."
            return render_template('complaints_form.html', error=error, success=success)

        # Insert into DB
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO complaints (
                    network_resolved_complaints, 
                    network_pending_complaints, 
                    total_calls_network,
                    it_resolved_complaints, 
                    it_pending_complaints, 
                    total_calls_it,
                    total_hours_spend,
                    grand_total_calls
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                network_resolved,
                network_pending,
                total_calls_network,
                it_resolved,
                it_pending,
                total_calls_it,
                hours_spend,
                grand_total_calls
            ))
            conn.commit()
            success = "✅ Complaint data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template('complaints_form.html', success=success, error=error)

    # Handle GET
    return render_template('complaints_form.html')

# Complaints List Route
@app.route('/complaints_list', methods=['GET', 'POST'])
def complaints_list():
    records = []
    total_calls_netork = total_calls_it = grand_total_calls = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
    except Exception as e:
        print("error", e)
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM complaints")
        records = cursor.fetchall()

        if records:
            total_calls_netork = sum(int(r['network_resolved']) for r in records if r['network_pending'])
            total_calls_it = sum(int(r['it_resolved']) for r in records if r['it_pending'])
            grand_total_calls = sum(int(r['total_calls_netork']) for r in records if r['total_calls_it'])
        else:
            total_calls_netork
            total_calls_it
            grand_total_calls

    except Exception as e:
        print("Error fetching complaints records:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return render_template('complaints_list.html', records=records, total_calls_netork=total_calls_netork, total_calls_it=total_calls_it)

# Route to delete a complaints
@app.route('/delete_complaints_form/<int:id>', methods=['POST'])
def delete_complaints_form(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM complaints WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Complaint deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('complaints_list'))

# Route to edit a complaints form
@app.route('/edit_complaints_form/<int:id>', methods=['GET', 'POST'])
def edit_complaints_form(id):
    error = None
    success = None

    if request.method == 'POST':
        # ✅ Get form values
        try:
            network_resolved = int(request.form['network_resolved'])
            network_pending = int(request.form['network_pending'])
            total_calls_network = network_resolved + network_pending

            it_resolved = int(request.form['it_resolved'])
            it_pending = int(request.form['it_pending'])
            total_calls_it = it_resolved + it_pending

            grand_total_calls = total_calls_network + total_calls_it

            hours_spend = request.form['hours_spend']

            # ✅ Update the record in database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE complaints SET
                    network_resolved_complaints = %s, 
                    network_pending_complaints = %s, 
                    total_calls_network = %s,
                    it_resolved_complaints = %s, 
                    it_pending_complaints = %s, 
                    total_calls_it = %s,
                    total_hours_spend = %s,
                    grand_total_calls = %s
                WHERE id = %s
            """, (
                network_resolved,
                network_pending,
                total_calls_network,
                it_resolved,
                it_pending,
                total_calls_it,
                hours_spend,
                grand_total_calls,
                id
            ))
            conn.commit()
            success = "✅ Complaint data updated successfully."
        except Exception as e:
            error = f"❌ Failed to update data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # ✅ Return back to the list view or confirmation page
        return redirect(url_for('complaints_list', error=error, success=success))  # or render_template with success message

    else:
        # ✅ GET request: fetch existing data for the form
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM complaints WHERE id = %s", (id,))
            record = cursor.fetchone()

            if record is None:
                flash("❌ Record not found!", 'danger')
                return redirect(url_for('complaints_list'))

        except Exception as e:
            flash("❌ Error loading complaint record.", 'danger')
            print("Fetch error:", e)
            return redirect(url_for('complaints_list'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template('edit_complaints_form.html', record=record)

# Store Items submission Route
@app.route('/store_item', methods=['GET', 'POST'])
def store_item():
    success = None
    error = None
    items = []
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('store_item.html', items=[], error=error, success=success)
    
    if request.method == 'POST':
        Items_Name = request.form.get('Items_Name')
        pending_demands = request.form.get('pending_demands')
        select_month = request.form.get('select_month')
        demands_curnt_month = request.form.get('demands_curnt_month')
        selected_month = request.form.get('selected_month')
        issued_cunt_month = request.form.get('issued_cunt_month')
        total_hours_spend = request.form.get('total_hours_spend')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO store_items (
                    items_name, 
                    pending_dmands, 
                    select_month, 
                    demands_of_current_month, 
                    selected_month, 
                    issued_of_current_month, 
                    total_hours_spend
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,(
                Items_Name,
                pending_demands,
                select_month,
                demands_curnt_month,
                selected_month,
                issued_cunt_month,
                total_hours_spend
            ))
            conn.commit()
            success = "✅ Items data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('store_item.html', items=items, success=success, error=error)

# store item list route
@app.route('/store_item_list', methods=['GET'])
def store_item_list():
    item_name = request.args.get('item_name', default='')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch items from item table
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()

        # Filter store_items based on selected item_name
        if item_name:
            cursor.execute("SELECT * FROM store_items WHERE items_name LIKE %s", ('%' + item_name + '%',))
        else:
            cursor.execute("SELECT * FROM store_items")

        records = cursor.fetchall()

    except Exception as e:
        print("Error:", e)
        items = []
        records = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("store_item_list.html", records=records, item_name=item_name, items=items)

# Route to delete a complaints
@app.route('/delete_store_item_list/<int:id>', methods=['POST'])
def delete_store_item_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM store_items WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Store items deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('store_item_list'))

# Route to edit a complaints form
@app.route('/edit_store_item_list/<int:id>', methods=['GET', 'POST'])
def edit_store_item_list(id):
    error = None
    success = None
    items = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('edit_store_item_list.html', items=[], error=error, success=success)
    
    if request.method == 'POST':
        Items_Name = request.form.get('Items_Name')
        pending_demands = request.form.get('pending_demands')
        select_month = request.form.get('select_month')
        demands_curnt_month = request.form.get('demands_curnt_month')
        selected_month = request.form.get('selected_month')
        issued_cunt_month = request.form.get('issued_cunt_month')
        total_hours_spend = request.form.get('total_hours_spend')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE store_items SET
                   items_name = %s, 
                    pending_dmands = %s, 
                    select_month = %s, 
                    demands_of_current_month = %s, 
                    selected_month = %s, 
                    issued_of_current_month = %s, 
                    total_hours_spend = %s
                WHERE id = %s
            """, (
                Items_Name,
                pending_demands,
                select_month,
                demands_curnt_month,
                selected_month,
                issued_cunt_month,
                total_hours_spend,
                id
            ))
            conn.commit()
            success = "✅ Store items data updated successfully."
        except Exception as e:
            error = f"❌ Failed to update data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # ✅ Return back to the list view or confirmation page
        return redirect(url_for('store_item_list', error=error, success=success))  # or render_template with success message

    else:
        # ✅ GET request: fetch existing data for the form
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM store_items WHERE id = %s", (id,))
            record = cursor.fetchone()

            if record is None:
                flash("❌ Record not found!", 'danger')
                return redirect(url_for('edit_store_item_list'))

        except Exception as e:
            flash("❌ Error loading complaint record.", 'danger')
            print("Fetch error:", e)
            return redirect(url_for('edit_store_item_list'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template('edit_store_item_list.html', record=record, items=items)
    
# Uploading Route
@app.route('/uploding_form', methods=['GET', 'POST'])
def uploding_form():
    success = None
    error = None

    if request.method == 'POST':
        particulars = request.form.get('particulars')
        res_person = request.form.get('res_person')
        previous_month = request.form.get('previous_month')
        previous_month_quantity = request.form.get('previous_month_quantity')
        current_month = request.form.get('current_month')
        current_month_quantity = request.form.get('current_month_quantity')
        hoursspend = request.form.get('hoursspend')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO uploding (
                    particulars, 
                    reserve_person, 
                    previous_month, 
                    previous_month_quantity, 
                    current_month, 
                    current_month_quantity, 
                    hoursspend
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,(
                particulars, 
                res_person,
                previous_month,
                previous_month_quantity,
                current_month,
                current_month_quantity,
                hoursspend
            ))
            conn.commit()
            success = "✅ Uploading data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('uploding_form.html', success=success, error=error)

# uploding list
@app.route('/uploding_list', methods=['GET', 'POST'])
def uploding_list():
    previous_month = request.args.get('previous_month', default='')
    conn = None
    cursor = None
    records = []
    total_previous_month_quantity = 0
    total_current_month_quantity = 0
    total_hours_spend = 0
    months = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # For dropdown
        cursor.execute("SELECT DISTINCT previous_month FROM uploding")
        months = cursor.fetchall()

        # Filtered or full list
        if previous_month:
            cursor.execute("SELECT * FROM uploding WHERE previous_month = %s", (previous_month,))
        else:
            cursor.execute("SELECT * FROM uploding")
            records = cursor.fetchall()

        # Totals
        total_previous_month_quantity = sum(int(r['previous_month_quantity']) for r in records if r['previous_month_quantity'])
        total_current_month_quantity = sum(int(r['current_month_quantity']) for r in records if r['current_month_quantity'])
        total_hours_spend = sum(int(r['hoursspend']) for r in records if r['hoursspend'])

    except Exception as e:
        print("Error fetching uploading items:", e)
        records = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'uploding_list.html',
        records=records,
        previous_month=previous_month,
        months=months,
        total_previous_month_quantity=total_previous_month_quantity,
        total_current_month_quantity=total_current_month_quantity,
        total_hours_spend=total_hours_spend
    )

# Route to delete uploading item
@app.route('/delete_uploding_item/<int:id>', methods=['POST'])
def delete_uploading_item(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uploding WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Uploadig item deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('uploding_list'))

# Route to edit_uploading_item
@app.route('/edit_uploading_item/<int:id>', methods=['GET', 'POST'])
def edit_uploading_item(id):
    error = None
    success = None

    if request.method == 'POST':
        particulars = request.form.get('particulars')
        res_person = request.form.get('res_person')
        previous_month = request.form.get('previous_month')
        previous_month_quantity = request.form.get('previous_month_quantity')
        current_month = request.form.get('current_month')
        current_month_quantity = request.form.get('current_month_quantity')
        hoursspend = request.form.get('hoursspend')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE uploding SET 
                    particulars = %s, 
                    reserve_person = %s, 
                    previous_month = %s, 
                    previous_month_quantity = %s, 
                    current_month = %s, 
                    current_month_quantity = %s, 
                    hoursspend = %s
                WHERE id = %s
            """,(
                particulars, 
                res_person,
                previous_month,
                previous_month_quantity,
                current_month,
                current_month_quantity,
                hoursspend,
                id
            ))
            conn.commit()
            flash("✅ Uploding Data updated successfully.", 'success')
        except Exception as e:
            flash("❌ Error updating uploading data.", 'danger')
            print("Update error:", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('uploding_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM uploding WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error uploading item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_uploading_item.html', record=record)

# Software form submission Route
@app.route('/softwareform', methods=['GET', 'POST'])
def softwareform():
    success = None
    error = None

    if request.method == 'POST':
        activities = request.form.get('activities')
        no_of_software = request.form.get('no_of_software')
        no_of_team_member = request.form.get('no_of_team_member')
        working_hours = request.form.get('working_hours')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO software_form (
                    activities, 
                    no_of_software_under_development, 
                    no_of_team_member, 
                    working_hours_during_month 
                ) VALUES (%s, %s, %s, %s)
            """,(
                activities, 
                no_of_software,
                no_of_team_member,
                working_hours
            ))
            conn.commit()
            success = "✅ Software data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('softwareform.html', success=success, error=error)

# Software form List Route
@app.route('/softwareform_list', methods=['GET', 'POST'])
def softwareform_list():
    filter_activities = request.args.get('activities', default='')
    records = []
    total_working_hours = 0
    activities_list = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get distinct activity names for dropdown
        cursor.execute("SELECT DISTINCT activities FROM software_form")
        activities_list = cursor.fetchall()

        # Fetch records based on filter
        if filter_activities:
            cursor.execute("SELECT * FROM software_form WHERE activities = %s", (filter_activities,))
        else:
            cursor.execute("SELECT * FROM software_form")

        records = cursor.fetchall()

        total_working_hours = sum(int(r['working_hours_during_month']) for r in records if r['working_hours_during_month'])

    except Exception as e:
        print("Error fetching software items:", e)
        records = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'softwareform_list.html',
        records=records,
        activities=activities_list,
        selected_activity=filter_activities,
        total_working_hours=total_working_hours
    )

# Route to delete software item
@app.route('/delete_softwareform_list/<int:id>', methods=['POST'])
def delete_softwareform_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM software_form WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Software item deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('softwareform_list'))

# Route to edit software item
@app.route('/edit_softwareform_list/<int:id>', methods=['GET', 'POST'])
def edit_softwareform_list(id):
    error = None
    success = None

    if request.method == 'POST':
        activities = request.form.get('activities')
        no_of_software = request.form.get('no_of_software')
        no_of_team_member = request.form.get('no_of_team_member')
        working_hours = request.form.get('working_hours')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE software_form SET
                    activities = %s, 
                    no_of_software_under_development = %s, 
                    no_of_team_member = %s, 
                    working_hours_during_month = %s
                WHERE id = %s
            """,(
                activities, 
                no_of_software,
                no_of_team_member,
                working_hours,
                id
            ))
            conn.commit()
            flash("✅ Software Data updated successfully.", 'success')
        except Exception as e:
            flash("❌ Error updating software data.", 'danger')
            print("Update error:", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('softwareform_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM software_form WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update software item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_softwareform_list.html', record=record)

# Core Software Form
@app.route('/coresoftwareform', methods=['GET', 'POST'])
def coresoftwareform():
    success = None
    error = None

    if request.method == 'POST':
        coresoftware = request.form.get('coresoftware')
        module = request.form.get('module')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO core_software (
                    core_software, 
                    modules 
                ) VALUES (%s, %s)
            """,(
                coresoftware, 
                module
            ))
            conn.commit()
            success = "✅ Core software data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template(
        'coresoftwareform.html', 
        success=success, 
        error=error, 
    )

# Core Software List
@app.route('/core_software_form_list', methods=['GET', 'POST'])
def core_software_form_list():
    filter_core_software = request.args.get('core_software', default='')
    records = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT core_software FROM core_software")
        core_software_list = cursor.fetchall()

        if filter_core_software:
            cursor.execute("SELECT * FROM core_software WHERE core_software = %s", (filter_core_software,))
        else:
            cursor.execute("SELECT * FROM core_software")

        records = cursor.fetchall()
    except Exception as e:
        print("Error fetching software items:", e)
        records = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'core_software_form_list.html', 
        records=records, 
        filter_core_software=filter_core_software,
        core_software_list=core_software_list
        )

# Core Software Form delete
@app.route('/delete_core_software_form_list/<int:id>', methods=['GET', 'POST'])
def delete_core_software_form_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM core_software WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Core Software deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('core_software_form_list'))

# Core Software Form edit
@app.route('/edit_core_software_form_list/<int:id>', methods=['GET', 'POST'])
def edit_core_software_form_list(id):
    success = None
    error = None

    if request.method == 'POST':
        coresoftware = request.form.get('coresoftware')
        module = request.form.get('module')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE core_software SET
                    core_software = %s, 
                    modules = %s 
                WHERE id = %s
            """,(
                coresoftware, 
                module,
                id
            ))
            conn.commit()
            success = "✅ Core software data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for('core_software_form_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM core_software WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update core software item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_core_software_form_list.html', record=record)

# Software complaints Route
@app.route('/softwarecomplainet', methods=['GET', 'POST'])
def softwarecomplainet():
    success = None
    error = None

    if request.method == 'POST':
        softwares = request.form.get('softwares')
        remarks = request.form.get('remarks')
        totalcomplaints = request.form.get('totalcomplaints')
        resolved = request.form.get('resolved')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO software_complaints (
                    software_name,
                    description,
                    total_complaints,
                    resolved
                ) VALUES (%s, %s, %s, %s)
            """,(
                softwares,
                remarks,
                totalcomplaints,
                resolved
            ))
            conn.commit()
            success = "✅ Core software data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('softwarecomplainet.html', success=success, error=error)

# Software complaints List
@app.route('/softwarecomplainet_list', methods=['GET', 'POST'])
def softwarecomplainet_list():
    records = []
    softwarecomplainet_list = []
    filter_software_name = request.args.get('software_name', default='')
    grand_total_complaints = 0
    total_resolved_complaints = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT software_name FROM software_complaints")
        softwarecomplainet_list = cursor.fetchall()
    except Exception as e:
        print("Error fetching software items:", e)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        if filter_software_name:
            cursor.execute("SELECT * FROM software_complaints WHERE software_name = %s", (filter_software_name,))
        else:
            cursor.execute("SELECT * FROM software_complaints")

        records = cursor.fetchall()

        if records:
            grand_total_complaints = sum(int(r['total_complaints']) for r in records if r ['total_complaints'])
            total_resolved_complaints = sum(int(r['resolved']) for r in records if r ['resolved'])
        else:
            grand_total_complaints = 0
            total_resolved_complaints = 0
    except Exception as e:
        print("Error fetching software items:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'softwarecomplainet_list.html', 
        records=records, 
        softwarecomplainet_list=softwarecomplainet_list,
        grand_total_complaints=grand_total_complaints, 
        total_resolved_complaints=total_resolved_complaints,
        filter_software_name=filter_software_name
    )

# Software complaints delete
@app.route('/delete_softwarecomplainet/<int:id>', methods=['POST'])
def delete_softwarecomplainet(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM software_complaints WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Software data deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('softwarecomplainet_list'))

# Software complaints edit
@app.route('/edit_softwarecomplainet_list/<int:id>', methods=['GET', 'POST'])
def edit_softwarecomplainet_list(id):
    success = None
    error = None

    if request.method == 'POST':
        softwares = request.form.get('softwares')
        remarks = request.form.get('remarks')
        totalcomplaints = request.form.get('totalcomplaints')
        resolved = request.form.get('resolved')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE software_complaints SET
                    software_name = %s, 
                    description = %s, 
                    total_complaints = %s, 
                    resolved = %s
                WHERE id = %s
            """,(
                softwares, 
                remarks,
                totalcomplaints,
                resolved,
                id
            ))
            conn.commit()
            success = "✅ software data updated successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for('softwarecomplainet_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM software_complaints WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update core software item.", 'danger')
        print("Fetch error:", e)
        record = []
    finally:
        cursor.close()
        conn.close()
    return render_template('edit_softwarecomplainet_list.html', record=record)

# Meetings Route
@app.route('/meetingform', methods=['GET', 'POST'])
def meetingform():
    success = None
    error = None

    if request.method == 'POST':
        sections = request.form.get('sections')
        meetings = request.form.get('meeting')
        internal = request.form.get('internal')
        external = request.form.get('external')
        hoursspend = request.form.get('hoursspend')
        remarks = request.form.get('remarks')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO meetings (
                    sections,
                    meetings,
                    internal,
                    external,
                    hours_spend,
                    remarks
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """,(
                sections,
                meetings,
                internal,
                external,
                hoursspend,
                remarks
            ))
            conn.commit()
            success = "✅ meetings data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('meetingform.html', success=success, error=error)

# Meetings List
@app.route('/meetingform_list', methods=['GET', 'POST'])
def meetingform_list():
    selected_section = request.args.get('sections', default='')
    sections_list = []
    records = []
    total_meetings = total_internal = total_external = total_hours_spend = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT sections FROM meetings")
        sections_list = cursor.fetchall()

        # Fetch filtered meetings
        if selected_section:
            cursor.execute("SELECT * FROM meetings WHERE sections = %s", (selected_section,))
        else:
            cursor.execute("SELECT * FROM meetings")
        records = cursor.fetchall()

        if records:
            total_meetings = sum(int(r['meetings']) for r in records if r ['meetings'])
            total_internal = sum(int(r['internal']) for r in records if r ['internal'])
            total_external = sum(int(r['external']) for r in records if r ['external'])
            total_hours_spend = sum(int(r['hours_spend']) for r in records if r ['hours_spend'])
        else:
            total_meetings = 0
            total_internal = 0
            total_external = 0
            total_hours_spend = 0
    except Exception as e:
        print("Error fetching meetings data:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'meetingform_list.html',
        records=sections_list,
        filter_sections=records,
        selected_section=selected_section,
        total_meetings =total_meetings,
        total_internal =total_internal,
        total_external =total_external,
        total_hours_spend=total_hours_spend
    )

# Meetings delete

@app.route('/delete_meetingform_list/<int:id>', methods=['GET', 'POST'])
def delete_meetingform_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM meetings WHERE id = %s", (id,))
        conn.commit()
        flash("✅ Meetings deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting meetings.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('meetingform_list'))

# Meetings edit
@app.route('/edit_meetingform_list/<int:id>', methods=['GET', 'POST'])
def edit_meetingform_list(id):
    success = None
    error = None

    if request.method == 'POST':
        sections = request.form.get('sections')
        meetings = request.form.get('meeting')
        internal = request.form.get('internal')
        external = request.form.get('external')
        hoursspend = request.form.get('hoursspend')
        remarks = request.form.get('remarks')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE meetings SET
                    sections = %s,
                    meetings = %s,
                    internal = %s,
                    external = %s,
                    hours_spend = %s,
                    remarks = %s
                WHERE id = %s
            """,(
                sections,
                meetings,
                internal,
                external,
                hoursspend,
                remarks,
                id
            ))
            conn.commit()
            success = "✅meetings data updated successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for('meetingform_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM meetings WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update meetings item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()
    return render_template('edit_meetingform_list.html', record=record)

# Network route
@app.route('/networkform', methods=['GET', 'POST'])
def networkform():
    success = None
    error = None

    if request.method == 'POST':
        item = request.form.get('item')
        downitem = request.form.get('downitem')
        uptime = request.form.get('uptime')
        remarks = request.form.get('remarks')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO network (
                    item, 
                    down_time,
                    up_time_percentage,  
                    remarks
                ) VALUES (%s, %s, %s, %s)
            """,(
                item,
                downitem,
                uptime,
                remarks
            ))
            conn.commit()
            success = "✅ network data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('networkform.html', success=success, error=error)

# Network List
@app.route('/networkform_list', methods=['GET', 'POST'])
def networkform_list():
    selected_item = request.args.get('item', default='')  # filter value from query params
    network_list = []  # for dropdown values
    records = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get dropdown values
        cursor.execute("SELECT DISTINCT item FROM network")
        network_list = cursor.fetchall()

        # Get table records
        if selected_item:
            cursor.execute("SELECT * FROM network WHERE item = %s", (selected_item,))
        else:
            cursor.execute("SELECT * FROM network")

        records = cursor.fetchall()

    except Exception as e:
        print("Error fetching network items:", e)
        records = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'networkform_list.html',
        records=records,
        network_list=network_list,
        selected_item=selected_item
    )

# Network delete
@app.route('/delete_networkform_list/<int:id>', methods=['GET', 'POST'])
def delete_networkform_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM network WHERE id = %s", (id,))
        conn.commit()
        flash("✅ network deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
        return redirect(url_for('networkform_list'))
    
# Network edit
@app.route('/edit_networkform_list/<int:id>', methods=['GET', 'POST'])
def edit_networkform_list(id):
    success = None
    error = None

    if request.method == 'POST':
        item = request.form.get('item')
        downitem = request.form.get('downitem')
        uptime = request.form.get('uptime')
        remarks = request.form.get('remarks')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE network SET
                    item = %s, 
                    down_time = %s,
                    up_time_percentage = %s,  
                    remarks = %s
                WHERE id = %s
            """,(
                item,
                downitem,
                uptime,
                remarks,
                id
            ))
            conn.commit()
            success = "✅ meetings data updated successfully."
        except Exception as e:
            error = f"❌ Failed to update data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for('networkform_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM network WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update network item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()
    return render_template('edit_networkform_list.html', record=record)

# PMIS Route
@app.route('/pmisreport', methods=['GET', 'POST'])
def pmisreport():
    success = None
    error = None
    progress_percentage = 0
    drone_video_percentage = 0
    total_packages = monthly_progress = drone_video = 0
    records = []

    if request.method == 'POST':
        total_packages = int(request.form.get('totalpackages'))
        monthly_progress = int(request.form.get('monthlyprogress'))
        drone_video = int(request.form.get('dronevideo'))

        # Calculate percentages after getting form data
        progress_percentage = int(monthly_progress / total_packages * 100) if total_packages > 0 else 0
        drone_video_percentage = int(drone_video / total_packages * 100) if total_packages > 0 else 0

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO pmis (
                    total_packages,
                    monthly_progress,
                    drone_video,
                    progress_percentage,
                    drone_video_percentage
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                total_packages,
                monthly_progress,
                drone_video,
                progress_percentage,
                drone_video_percentage
            ))
            conn.commit()
            success = "✅ PMIS data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Fetch existing data for display
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pmis")
        records = cursor.fetchall()
    except Exception as e:
        print("Error fetching pmis items:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'pmisreport.html',
        success=success,
        error=error,
        drone_video_percentage=drone_video_percentage,
        progress_percentage=progress_percentage,
        records=records
    )

# PMIS List
@app.route('/pmisreport_list', methods=['GET', 'POST'])
def pmisreport_list():
    records = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pmis")
        records = cursor.fetchall()

        # Calculate percentages for each record with 2 decimal places
        for r in records:
            total_packages = r['total_packages'] or 0
            monthly_progress = r['monthly_progress'] or 0
            drone_video = r['drone_video'] or 0

            r['progress_percentage'] = round((monthly_progress / total_packages * 100)) if total_packages > 0 else 0
            r['drone_video_percentage'] = round((drone_video / total_packages * 100)) if total_packages > 0 else 0

    except Exception as e:
        print("Error fetching pmis items:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'pmisreport_list.html',
        records=records
    )

# PMIS delete
@app.route('/delete_pmisreport_list/<int:id>', methods=['GET', 'POST'])
def delete_pmisreport_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pmis WHERE id = %s", (id,))
        conn.commit()
        flash("✅ pmis data deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('pmisreport_list'))

# PMIS edit
@app.route('/edit_pmisreport_list/<int:id>', methods=['GET', 'POST'])
def edit_pmisreport_list(id):
    success = None
    error = None

    if request.method == 'POST':
        total_packages = request.form.get('totalpackages')
        monthly_progress = request.form.get('monthlyprogress')
        drone_video = request.form.get('dronevideo')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pmis SET
                    total_packages = %s,
                    monthly_progress = %s,
                    drone_video = %s
                WHERE id = %s
            """,(
                total_packages, 
                monthly_progress,
                drone_video,
                id
            ))
            conn.commit()
            success = "✅ pmis data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for('pmisreport_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pmis WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update pmis item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()
    return render_template('edit_pmisreport_list.html', record=record)

# Summarize Route
@app.route('/summarisereport', methods=['GET', 'POST'])
def summarisereport():
    success = None
    error = None

    if request.method == 'POST':
        procurement = request.form.get('procurement')
        current_month = request.form.get('current_month')
        available_hours = request.form.get('availablehours')
        working_strength = request.form.get('workingstrength')
        hours_worked = request.form.get('hoursworked')
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO summarize (
                    procurement_activities,
                    current_month,
                    available_hours,
                    working_strength,
                    hours_worked
                ) VALUES (%s, %s, %s, %s, %s)
            """,(
                procurement,
                current_month,
                available_hours,
                working_strength,
                hours_worked
            ))
            conn.commit()
            success = "✅ summarize data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('summarisereport.html' , success=success, error=error)

# Summarize List
@app.route('/summarisereport_list', methods=['GET', 'POST'])
def summarisereport_list():
    records = []
    procurement_list = []
    filter_procurement_activities = request.args.get('procurement_activities', default='')
    total_available_hours = total_working_strength = total_hours_worked = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT procurement_activities FROM summarize")
        procurement_list = cursor.fetchall()
    except Exception as e:
        print("Error fetching procurement activities:", e)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        if filter_procurement_activities:
            cursor.execute("SELECT * FROM summarize WHERE procurement_activities = %s", (filter_procurement_activities,))
        else:
            cursor.execute("SELECT * FROM summarize")

        records = cursor.fetchall()

        if records:
            total_available_hours = sum(int(r['available_hours']) for r in records if r['available_hours'])
            total_working_strength = sum(int(r['working_strength']) for r in records if r['working_strength'])
            total_hours_worked = sum(int(r['hours_worked']) for r in records if r['hours_worked'])
    except Exception as e:
        print("Error fetching summarize items:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'summarisereport_list.html',
        total_available_hours=total_available_hours,
        total_working_strength=total_working_strength,
        total_hours_worked=total_hours_worked,
        procurement_list=procurement_list,  # for dropdown
        records=records  # for table
    )

# Summarize delete
@app.route('/delete_summarisereport_list/<int:id>', methods=['GET', 'POST'])
def delete_summarisereport_list(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM summarize WHERE id = %s", (id,))
        conn.commit()
        flash("✅ summarize deleted successfully.", 'success')
    except Exception as e:
        flash("❌ Error deleting item.", 'danger')
        print("Delete error:", e)
    finally:
        cursor.close()
        conn.close()
    return render_template('summarisereport_list.html')

# Summarize edit
@app.route('/edit_summarisereport_list/<int:id>', methods=['GET', 'POST'])
def edit_summarisereport_list(id):
    success = None
    error = None

    if request.method == 'POST':
        procurement = request.form.get('procurement')
        current_month = request.form.get('current_month')
        available_hours = request.form.get('availablehours')
        working_strength = request.form.get('workingstrength')
        hours_worked = request.form.get('hoursworked')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE summarize SET
                    procurement_activities = %s, 
                    current_month = %s, 
                    available_hours = %s,
                    working_strength = %s, 
                    hours_worked = %s 
                WHERE id = %s
            """,(
                procurement, 
                current_month,
                available_hours,
                working_strength,
                hours_worked,
                id
            ))
            conn.commit()
            success = "✅ summarize data inserted successfully."
        except Exception as e:
            error = f"❌ Failed to insert data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for('summarisereport_list', error=error, success=success))

    # GET method
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM summarize WHERE id = %s", (id,))
        record = cursor.fetchone()
    except Exception as e:
        flash("❌ Error update summarize item.", 'danger')
        print("Fetch error:", e)
        record = None
    finally:
        cursor.close()
        conn.close()
    return render_template('edit_summarisereport_list.html', record=record)

if __name__ == '__main__':
    app.run(debug=True)