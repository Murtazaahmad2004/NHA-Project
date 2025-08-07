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

    return render_template("procurement_item_list.html", records=records, item_name=item_name, items=items)

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
                    res_person, 
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
    return render_template('uploding_list.html')

# Meetings Route
@app.route('/meetingform', methods=['GET', 'POST'])
def meetingform():
    return render_template('meetingform.html')

# Network route
@app.route('/networkform', methods=['GET', 'POST'])
def networkform():
    return render_template('networkform.html')

# PMIS Route
@app.route('/pmisreport', methods=['GET', 'POST'])
def pmisreport():
    return render_template('pmisreport.html')

# Software complaints Route
@app.route('/softwarecomplainet', methods=['GET', 'POST'])
def softwarecomplainet():
    return render_template('softwarecomplainet.html')

# Software form submission Route
@app.route('/softwareform', methods=['GET', 'POST'])
def softwareform():
    return render_template('softwareform.html')

# Summarize Route
@app.route('/summarisereport', methods=['GET', 'POST'])
def summarisereport():
    return render_template('summarisereport.html')

# Core Software Form
@app.route('/coresoftwareform', methods=['GET', 'POST'])
def coresoftwareform():
    return render_template('coresoftwareform.html')

if __name__ == '__main__':
    app.run(debug=True)