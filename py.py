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
    return render_template('form.html')

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

@app.route('/budget_list', methods=['GET'])
def show_budget_list():
    selected_year = request.args.get('financial_year')
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        if selected_year:
            cursor.execute("SELECT * FROM budget WHERE financial_year = %s", (selected_year,))
        else:
            cursor.execute("SELECT * FROM budget")
        
        records = cursor.fetchall()
    except Exception as e:
        print("Error fetching data:", e)
        records = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('budget_list.html', records=records, selected_year=selected_year)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budget WHERE id = %s", (id,))
        conn.commit()
        flash('Data has been deleted successfully.', 'success')
    except Exception as e:
        flash('Error deleting data.', 'danger')
        print("Error deleting record:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('show_budget_list'))  # or whatever your list route is called

if __name__ == '__main__':
    app.run(debug=True)