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

# Form for budget submission
@app.route('/form', methods=['GET', 'POST'])
def form():
    error = None
    success = None

    if request.method == 'POST':
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
            return render_template('form.html', error=error)

        # Validate date format
        try:
            year, month = map(int, budgetmonth.split('-'))
            reporting_month_last_day = calendar.monthrange(year, month)[1]
        except:
            error = "⚠️ Invalid month format. Use YYYY-MM."
            return render_template('form.html', error=error)

        remaining_budget = totalbudget_val - budgetupto_val

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

        return render_template('form.html', success=success, error=error)
    return render_template('form.html')

# Route to show budget list
@app.route('/budget_list')
def show_budget_list():
    selected_year = request.args.get('financial_year')
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        if selected_year:
            cursor.execute("SELECT * FROM budget WHERE financial_year = %s", (selected_year,))
        else:
            cursor.execute("SELECT * FROM budget ORDER BY id DESC")
        records = cursor.fetchall()
    except Exception as e:
        records = []
        print("Error fetching records:", e)
    finally:
        cursor.close()
        conn.close()
    return render_template('budget_list.html', records=records, selected_year=selected_year)

# Route to delete a budget record
@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budget WHERE id = %s", (id,))
        conn.commit()
        flash("Record deleted successfully.", 'success')
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
            flash("Record updated successfully.", 'success')
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

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert all non-empty item names
            for item in item_names:
                item = item.strip()
                if item:
                    cursor.execute("INSERT INTO item (items_name) VALUES (%s)", (item,))

            conn.commit()
            success = f"✅ {len([i for i in item_names if i.strip()])} items submitted successfully!"
        except Exception as e:
            error = f"❌ Failed to insert items: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('head_form.html', success=success, error=error)

# head/items List route
@app.route('/item_list')
def item_list():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM item")
        records = cursor.fetchall()
    except Exception as e:
        records = []
        print("Error fetching items:", e)
    finally:
        cursor.close()
        conn.close()
    
    return render_template('item_list.html', records=records)

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
        cursor.execute("SELECT id, items_name FROM item")
        items = cursor.fetchall()
        cursor.close()
    except Exception as e:
        error = f"Error fetching items: {e}"
        return render_template('repair_maintenance.html', items=[], error=error, success=success)
    
    if request.method == 'POST':
        item_name = request.form['itemname']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("UPDATE item SET items_name = %s WHERE id = %s", (item_name, id))
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
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM procurement")
        records = cursor.fetchall()
    except Exception as e:
        records = []
        print("Error fetching procurement items:", e)
    finally:
        cursor.close()
        conn.close()

    return render_template('procurement_item_list.html', records=records)

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
        return render_template('repair_maintenance.html', items=[], error=error, success=success)
    
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
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO repair_maintenance (item_name, unit_in_house, units_externals, 
                           hours_spend_in_house, days_externals, expenditure)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (itemlist, units, unit, hoursspend, days, expenditure))
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
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM repair_maintenance")
        records = cursor.fetchall()
    except Exception as e:
        records = []
        print("Error fetching repair and maintenance items:", e)
    finally:
        cursor.close()
        conn.close()

    return render_template('repair_maintenance_list.html', records=records)

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
        itemlist = request.form['itemlist']
        units = request.form['units']
        hoursspend = request.form['hoursspend']
        unit = request.form['unit']
        days = request.form['days']
        expenditure = request.form['expenditure']
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
                    expenditure = %s
                WHERE id = %s
            """, (itemlist, units, hoursspend, unit, days, expenditure, id))
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

    return render_template('edit_repair_maintenance.html', items=items, record=record)

if __name__ == '__main__':
    app.run(debug=True)