(function () {
  if (typeof Chart === 'undefined') {
    return;
  }

  var charts = [];

  Chart.defaults.font.family = '"Heebo", "Roboto", sans-serif';
  Chart.defaults.animation.duration = 850;
  Chart.defaults.animation.easing = 'easeOutQuart';

  function isDarkTheme() {
    return document.documentElement.classList.contains('ma-theme-dark')
      || document.body.getAttribute('data-theme') === 'dark';
  }

  function getTheme() {
    if (isDarkTheme()) {
      return {
        muted: '#9aadc0',
        grid: 'rgba(255, 255, 255, 0.06)',
        tooltip: {
          backgroundColor: '#1e2736',
          titleColor: '#edf2f7',
          bodyColor: '#9aadc0',
        },
        metrics: [
          { label: 'Accuracy', color: '#8faed4' },
          { label: 'Precision', color: '#e85a7f' },
          { label: 'Recall', color: '#5eb8b4' },
          { label: 'F1 Score', color: '#d4a574' },
        ],
      };
    }

    return {
      muted: '#6f8ba4',
      grid: 'rgba(34, 58, 102, 0.08)',
      tooltip: {
        backgroundColor: '#223a66',
        titleColor: '#ffffff',
        bodyColor: '#e8eef5',
      },
      metrics: [
        { label: 'Accuracy', color: '#223a66' },
        { label: 'Precision', color: '#e12454' },
        { label: 'Recall', color: '#48a9a6' },
        { label: 'F1 Score', color: '#f4a261' },
      ],
    };
  }

  function metricValues(algorithms, key) {
    return algorithms.map(function (algo) {
      return algo[key];
    });
  }

  function createMetricsChart(canvas, algorithms) {
    var theme = getTheme();
    Chart.defaults.color = theme.muted;

    var datasets = theme.metrics.map(function (metric, index) {
      var keys = ['accuracy', 'precision', 'recall', 'f1_score'];
      return {
        label: metric.label,
        data: metricValues(algorithms, keys[index]),
        backgroundColor: metric.color,
        hoverBackgroundColor: metric.color,
        borderRadius: 8,
        borderSkipped: false,
        maxBarThickness: 42,
      };
    });

    return new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: algorithms.map(function (algo) {
          return algo.name;
        }),
        datasets: datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            position: 'bottom',
            align: 'start',
            labels: {
              padding: 18,
              boxWidth: 10,
              boxHeight: 10,
              usePointStyle: true,
              pointStyle: 'circle',
              color: theme.muted,
            },
          },
          tooltip: {
            backgroundColor: theme.tooltip.backgroundColor,
            titleColor: theme.tooltip.titleColor,
            bodyColor: theme.tooltip.bodyColor,
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            boxPadding: 4,
            callbacks: {
              label: function (ctx) {
                return ' ' + ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(2) + '%';
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
              drawBorder: false,
            },
            ticks: {
              color: theme.muted,
              font: {
                size: 12,
                weight: '500',
              },
            },
          },
          y: {
            beginAtZero: true,
            suggestedMax: 100,
            ticks: {
              color: theme.muted,
              stepSize: 20,
              callback: function (value) {
                return value + '%';
              },
            },
            grid: {
              color: theme.grid,
              drawBorder: false,
            },
          },
        },
      },
    });
  }

  function initChart(canvasId, dataElId) {
    var dataEl = document.getElementById(dataElId);
    var canvas = document.getElementById(canvasId);

    if (!dataEl || !canvas) {
      return null;
    }

    var algorithms = JSON.parse(dataEl.textContent);
    if (!algorithms.length) {
      return null;
    }

    return createMetricsChart(canvas, algorithms);
  }

  function buildCharts() {
    charts.forEach(function (chart) {
      chart.destroy();
    });
    charts = [];

    [
      ['algorithmComparisonChart', 'admin-algorithm-chart-data'],
      ['adminDashboardChart', 'admin-dashboard-chart-data'],
    ].forEach(function (pair) {
      var chart = initChart(pair[0], pair[1]);
      if (chart) {
        charts.push(chart);
      }
    });
  }

  buildCharts();
  document.addEventListener('portal-theme-change', buildCharts);
  document.addEventListener('dashboard-theme-change', buildCharts);
})();
