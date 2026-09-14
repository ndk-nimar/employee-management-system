/* Dashboard charts.
   The numbers are calculated in Django (employees/views.py::dashboard) and
   handed to the page with {{ value|json_script:"id" }}, which renders a
   <script type="application/json"> tag. Nothing is hard-coded here. */

(function () {
  "use strict";

  function readJSON(id) {
    var node = document.getElementById(id);
    if (!node) return null;
    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      console.error("Could not read chart data for", id, error);
      return null;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof Chart === "undefined") return;

    Chart.defaults.font.family = "Manrope, Segoe UI, system-ui, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = "#6a757d";

    buildDepartmentChart();
    buildStatusChart();
  });

  function buildDepartmentChart() {
    var canvas = document.getElementById("departmentChart");
    var labels = readJSON("department-labels");
    var values = readJSON("department-values");
    if (!canvas || !labels || !values || !labels.length) return;

    new Chart(canvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Employees",
            data: values,
            backgroundColor: "#2f8a79",
            hoverBackgroundColor: "#1f6f63",
            borderRadius: 6,
            maxBarThickness: 46,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#131d22",
            padding: 10,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
              label: function (context) {
                var count = context.parsed.y;
                return count + (count === 1 ? " employee" : " employees");
              },
            },
          },
        },
        scales: {
          x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: false } },
          y: {
            beginAtZero: true,
            ticks: { precision: 0, stepSize: 1 },
            grid: { color: "rgba(24,40,46,0.08)", drawBorder: false },
          },
        },
      },
    });
  }

  function buildStatusChart() {
    var canvas = document.getElementById("statusChart");
    var labels = readJSON("status-labels");
    var values = readJSON("status-values");
    if (!canvas || !labels || !values) return;

    new Chart(canvas, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            data: values,
            backgroundColor: ["#2f8a79", "#c9a24a", "#9aa5ab"],
            hoverOffset: 6,
            borderWidth: 2,
            borderColor: "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "62%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { usePointStyle: true, pointStyle: "circle", padding: 16, boxWidth: 8 },
          },
          tooltip: {
            backgroundColor: "#131d22",
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function (context) {
                var total = context.dataset.data.reduce(function (sum, n) {
                  return sum + n;
                }, 0);
                var share = total ? Math.round((context.parsed / total) * 100) : 0;
                return context.label + ": " + context.parsed + " (" + share + "%)";
              },
            },
          },
        },
      },
    });
  }
})();
