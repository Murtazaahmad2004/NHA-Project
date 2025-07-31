function confirmDelete() {
    return confirm("Are you sure you want to delete this record?");
}
function calculateRemaining() {
    const total = parseFloat(document.getElementById('totalbudget').value) || 0;
    const upto = parseFloat(document.getElementById('budgetupto').value) || 0;
    const remaining = total - upto;
    document.getElementById('remaining_budget').value = remaining.toFixed(2);
}

    const totalBudgetInput = document.getElementById('totalbudget');
    const budgetUptoInput = document.getElementById('budgetupto');
    const budgetMonthInput = document.getElementById('budgetmonth');
    const unitsInput = document.getElementById('units');
    const unitInput = document.getElementById('unit');

if (totalBudgetInput) totalBudgetInput.addEventListener('input', calculateRemaining);
if (budgetUptoInput) budgetUptoInput.addEventListener('input', calculateRemaining);

if (budgetMonthInput) {
    budgetMonthInput.addEventListener('change', function () {
    const value = this.value;
if (value) {
    const [year, month] = value.split('-').map(Number);
    const lastDay = new Date(year, month, 0);
    const dayOnly = lastDay.getDate();
    document.getElementById('lastday').value = dayOnly;
} else {
    document.getElementById('lastday').value = '';
}
});
}

function updateTotal() {
    const unitsInHouse = parseInt(unitsInput?.value) || 0;
    const unitsExternals = parseInt(unitInput?.value) || 0;
    const total = unitsInHouse + unitsExternals;
    const totalField = document.getElementById('total_items');
if (totalField) totalField.value = total;
}

if (unitsInput) unitsInput.addEventListener('input', updateTotal);
if (unitInput) unitInput.addEventListener('input', updateTotal);
updateTotal();

function addField() {
    const div = document.createElement('div');
    div.classList.add('form-group');
    div.innerHTML = `
    <input type="text" name="itemname[]" class="form-control" placeholder="Enter Item Name" required>
    `;
    document.getElementById('itemFields')?.appendChild(div);
}

const all_rows = document.querySelectorAll('#records tr');
const records_per_page = 2;
let page_number = 1;
const total_records = all_rows.length;
const total_pages = Math.ceil(total_records / records_per_page);

function DisplayRecords() {
const start_index = (page_number - 1) * records_per_page;
const end_index = start_index + records_per_page;

all_rows.forEach((row, index) => {
row.style.display = (index >= start_index && index < end_index) ? '' : 'none';
});
}

DisplayRecords();