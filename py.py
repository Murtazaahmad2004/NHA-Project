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

@app.route('/')
def home():
    return render_template('home.html')

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

@app.route('/head_form', methods=['GET', 'POST'])
def head_form():
    if request.method == 'POST':
        item_name = request.form.get('itemname')
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO item (
                items_name
            ) VALUES (%s)
        """, (
            item_name
        ))
        conn.commit()
        success = "✅ Items data submitted successfully!"
    except Exception as e:
        error = f"❌ Failed to insert data: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn():
            conn.close()
    return render_template('head_form.html', success=success, error=error)

if __name__ == '__main__':
    app.run(debug=True)