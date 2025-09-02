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
    const startyear = 2020;
    const endyear = currentyear + 1;
    let options = `<option value="">Select Financial Year</option>`;

    for(let year = startyear; year < endyear; year++){
      
        options += `<option value="${year}">${year}</option>`;
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
  const budgetMonthInput = document.getElementById("budgetmonth");
  const budgetUptoContainer = document.getElementById("budgetupto-container");

  budgetMonthInput.addEventListener("change", function () {
    const value = this.value; // e.g. "2025-04"
    if (!value) return;

    const [year, month] = value.split("-");
    const monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];
    const monthName = monthNames[parseInt(month) - 1];

    // Pehle purana field hata do (agar already add hua ho)
    budgetUptoContainer.innerHTML = "";

    // Naya field banao
    const formGroup = document.createElement("div");
    formGroup.classList.add("form-group");

    const label = document.createElement("label");
    label.setAttribute("for", "budgetupto");
    label.textContent = `Budget Up to ${monthName} ${year}:`;

    const input = document.createElement("input");
    input.type = "number";
    input.id = "budgetupto";
    input.name = "budgetupto";
    input.classList.add("form-control");
    input.placeholder = `Enter Budget up to ${monthName} ${year}`;
    input.required = true;

    formGroup.appendChild(label);
    formGroup.appendChild(input);
    budgetUptoContainer.appendChild(formGroup);
  });
});

let charts = {};
const rainbowColors = ["#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF","#FF9F40","#C9CBCF","#8DD17D","#FF6F61","#6A5ACD"];

function loadChart(chartId, chartType, chartLabel, chartJsType) {
  const month = document.getElementById("monthPicker").value;

  fetch(`/chart/${chartType}?month=${month}`)
    .then(res => res.json())
    .then(data => {
      if (charts[chartId]) charts[chartId].destroy();

      const ctx = document.getElementById(chartId).getContext("2d");

      charts[chartId] = new Chart(ctx, {
        type: chartJsType,
        data: {
          labels: data.labels,
          datasets: data.datasets.map((ds, i) => {
            if (chartJsType === "line") {
              return {...ds, borderColor: rainbowColors[i % rainbowColors.length], backgroundColor: "rgba(0,0,0,0)", borderWidth: 2, fill: false, tension: 0.2};
            }
            if (chartJsType === "doughnut" || chartJsType === "pie") {
              return {...ds, backgroundColor: rainbowColors.slice(0, ds.data.length), borderColor: "#fff", borderWidth: 1};
            }
            return {...ds, backgroundColor: rainbowColors.slice(0, ds.data.length), borderColor: "#fff", borderWidth: 1};
          })
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top", labels: { boxWidth: 20, padding: 15 } },
            title: { display: true, text: chartLabel, font: { size: 18 } },
            tooltip: { mode: "index", intersect: false }
          },
          scales: chartJsType !== "doughnut" && chartJsType !== "pie" ? {
            y: { beginAtZero: true, grid: { color: "#f0f0f0" } },
            x: { grid: { color: "#f0f0f0" } }
          } : {}
        }
      });
    })
    .catch(err => console.error("Chart Load Error:", err));
}

function loadAllCharts() {
  const chartsList = [
  {id: "budgetChart", type: "budget", chartJsType: "bar"},
  {id: "procurementChart", type: "procurement", chartJsType: "line"},
  {id: "repairChart", type: "repair_maintenance", chartJsType: "bar"},
  {id: "callsChart", type: "complaints", chartJsType: "line"},
  {id: "storeItemChart", type: "store_items", chartJsType: "bar"},
  {id: "uplodingChart", type: "uploding", chartJsType: "pie"},
  {id: "softwareFormChart", type: "software_form", chartJsType: "bar"},
  {id: "coreSoftwareChart", type: "core_software", chartJsType: "doughnut"},
  {id: "summarizeChart", type: "summarize", chartJsType: "bar"}
];

  chartsList.forEach(c => loadChart(c.id, c.type, c.title, c.chartJsType));
}

document.addEventListener("DOMContentLoaded", function() {
  loadAllCharts();
  document.getElementById("monthPicker").addEventListener("change", loadAllCharts);
});

function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);
  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  } else {
    input.type = "password";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  }
}