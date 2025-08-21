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
    <input type="number" name="quantity" class="form-control" placeholder="Quantity" required>
    `;
    document.getElementById('itemFields')?.appendChild(div);
}

function GenerateYearOptions() {
    const currentyear =  new Date().getFullYear();
    const startyear = 2018;
    let options = `<option value="">Select Financial Year</option>`;

    for(let year = startyear; year < currentyear; year++){
        const range = `${year} - ${year + 1}`;
        options += `<option value="${range}">${range}</option>`;
    }
    return options;
}

function AddField() {
    const div = document.createElement('div');
    div.classList.add('form-group');
    div.innerHTML = `
   <select name="financialyear[]" class="form-control" required>
        ${GenerateYearOptions()}
   </select>
    `;
    document.getElementById('financial_year')?.appendChild(div);
}

window.onload = function () {
    const selects = document.querySelectorAll('select[name="financialyear[]"]');
    selects.forEach(select => {
        select.innerHTML = GenerateYearOptions();
    });
};

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

const data = [];
    for (let i = 1; i <= 50; i++) {
    data.push(`Item ${i}`);
}

let currentPage = 1;
const rowsPerPage = 5;

function displayList(items, wrapper, rowsPerPage, page) {
    wrapper.innerHTML = "";
    page--;

    let start = rowsPerPage * page;
    let end = start + rowsPerPage;
    let paginatedItems = items.slice(start, end);

for (let i = 0; i < paginatedItems.length; i++) {
    let item = paginatedItems[i];
    let li = document.createElement("li");
    li.innerText = item;
    wrapper.appendChild(li);
}
}

function setupTablePagination(tableId, paginationId, rowsPerPage) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector("tbody");
    const rows = tbody.querySelectorAll("tr");
    const pagination = document.getElementById(paginationId);

    let currentPage = 1;
    const totalPages = Math.ceil(rows.length / rowsPerPage);

    function displayPage(page) {
        currentPage = page;
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? "" : "none";
        });

        renderPagination();
    }

    function renderPagination() {
        pagination.innerHTML = "";

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            if (i === currentPage) li.classList.add("active");

            const a = document.createElement("a");
            a.href = "#";
            a.textContent = i;
            a.addEventListener("click", function (e) {
                e.preventDefault();
                displayPage(i);
            });

            li.appendChild(a);
            pagination.appendChild(li);
        }
    }

    displayPage(1);
}

document.addEventListener("DOMContentLoaded", function () {
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
    setupTablePagination("budgetTable", "pagination", 5); // 5 rows per page
});

document.addEventListener("DOMContentLoaded", function () {

    function getRainbowColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            const hue = Math.floor((i / count) * 360); // distribute hue evenly
            colors.push(`hsl(${hue}, 70%, 50%)`);
        }
        return colors;
    }

    function loadChart(endpoint, canvasId, chartType = "line") {
        fetch(`/chart-data/${endpoint}`)
            .then(response => response.json())
            .then(data => {
                var ctx = document.getElementById(canvasId).getContext("2d");

                let chartColors = [];
                if (chartType === "pie" || chartType === "doughnut" || data.values.length > 1) {
                    chartColors = getRainbowColors(data.values.length);
                } else {
                    chartColors = ["rgb(54, 162, 235)"];
                }

                new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: data.label,
                            data: data.values,
                            backgroundColor: chartColors,
                            borderColor: chartColors,
                            fill: false,
                            lineTension: 0.2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            yAxes: [{ ticks: { beginAtZero: true } }]
                        }
                    }
                });
            })
            .catch(err => console.error(`Error loading ${endpoint} chart:`, err));
    }

    // Load charts dynamically
    loadChart("budget", "budgetChart", "line");
    loadChart("repair_maintenance", "repairChart", "bar");
    loadChart("complaints", "callsChart", "pie");
    loadChart("store_items", "storeItemChart", "line");
    loadChart("uploding", "uploadingChart", "bar");
    loadChart("software_form", "softwareFormChart", "pie");
    loadChart("core_software", "coreSoftwareChart", "line");
    loadChart("summarize", "summarizeChart", "bar");
});