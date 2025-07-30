function confirmDelete() {
    return confirm("Are you sure you want to delete this record?");
}

function calculateRemaining() {
    const total = parseFloat(document.getElementById('totalbudget').value) || 0;
    const upto = parseFloat(document.getElementById('budgetupto').value) || 0;
    const remaining = total - upto;
    document.getElementById('remaining_budget').value = remaining.toFixed(2);
}
    document.getElementById('totalbudget').addEventListener('input', calculateRemaining);
    document.getElementById('budgetupto').addEventListener('input', calculateRemaining);

document.getElementById('budgetmonth').addEventListener('change', function () {
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

function updateTotal() {
const unitsInHouse = parseInt(document.getElementById('units').value) || 0;
const unitsExternals = parseInt(document.getElementById('unit').value) || 0;
const total = unitsInHouse + unitsExternals;
document.getElementById('total_items').value = total;
}
document.getElementById('units').addEventListener('input', updateTotal);
document.getElementById('unit').addEventListener('input', updateTotal);

updateTotal();

function addField() {
    const div = document.createElement('div');
    div.classList.add('form-group');
    div.innerHTML = `
        <input type="text" name="itemname[]" class="form-control" placeholder="Enter Item Name" required>
    `;
    document.getElementById('itemFields').appendChild(div);
}

const total_records_tr = document.querySelectorAll('#records tr').length;
const records_per_page = 2;
const page_number = 1;
const total_records = total_records_tr.length;
const total_pages = Math.ceil(total_records / records_per_page);

function DisplayRecords(){
    let start_index = (page_number - 1) * records_per_page;
    let end_index = start_index + (records_per_page - 1);

    for (let i = start_index; i < end_index; i++){
        console.log(total_records_tr[i]);
    }
}