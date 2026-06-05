(function () {

  var dataEl = document.getElementById('dashboard-chart-data');

  if (!dataEl || typeof Chart === 'undefined') {

    return;

  }



  var data = JSON.parse(dataEl.textContent);

  var charts = [];



  Chart.defaults.font.family = 'Roboto, sans-serif';

  Chart.defaults.animation.duration = 900;

  Chart.defaults.animation.easing = 'easeOutQuart';



  function isDarkTheme() {

    return document.documentElement.classList.contains('ma-theme-dark')

      || document.body.getAttribute('data-theme') === 'dark';

  }



  function getTheme() {

    if (isDarkTheme()) {

      return {

        primary: '#8faed4',

        accent: '#e85a7f',

        muted: '#9aadc0',

        palette: ['#8faed4', '#e85a7f', '#5eb8b4', '#d4a574', '#9aadc0', '#6b8fc7'],

        grid: 'rgba(255, 255, 255, 0.05)',

        tooltip: {

          backgroundColor: '#1e2736',

          titleColor: '#edf2f7',

          bodyColor: '#9aadc0',

        },

        doughnutBorder: '#1e2736',

        pointBorder: '#1e2736',

      };

    }



    return {

      primary: '#223a66',

      accent: '#e12454',

      muted: '#6f8ba4',

      palette: ['#223a66', '#e12454', '#48a9a6', '#f4a261', '#6f8ba4', '#2d4f7c'],

      grid: 'rgba(34, 58, 102, 0.08)',

      tooltip: {

        backgroundColor: '#223a66',

        titleColor: '#fff',

        bodyColor: '#e8eef5',

      },

      doughnutBorder: '#fff',

      pointBorder: '#fff',

    };

  }



  function destroyCharts() {

    charts.forEach(function (chart) {

      chart.destroy();

    });

    charts = [];

  }



  function showEmpty(canvasId, show) {

    var canvas = document.getElementById(canvasId);

    var empty = document.getElementById(canvasId + '-empty');

    if (canvas) {

      canvas.style.display = show ? 'none' : 'block';

    }

    if (empty) {

      empty.style.display = show ? 'flex' : 'none';

    }

  }



  function makeGradient(ctx, colorStart, colorEnd) {

    var gradient = ctx.createLinearGradient(0, 0, 0, 260);

    gradient.addColorStop(0, colorStart);

    gradient.addColorStop(1, colorEnd);

    return gradient;

  }



  function percentLabel(value, values) {

    var total = values.reduce(function (sum, n) { return sum + n; }, 0);

    if (!total) {

      return '0%';

    }

    return Math.round((value / total) * 100) + '%';

  }



  function buildCharts() {

    destroyCharts();

    var theme = getTheme();



    Chart.defaults.color = theme.muted;



    var sharedTooltip = {

      backgroundColor: theme.tooltip.backgroundColor,

      titleColor: theme.tooltip.titleColor,

      bodyColor: theme.tooltip.bodyColor,

      padding: 12,

      cornerRadius: 8,

      displayColors: true,

      boxPadding: 4,

    };



    var gridStyle = {

      color: theme.grid,

      drawBorder: false,

    };



    if (data.has_activity) {

      showEmpty('activityChart', false);

      var activityCtx = document.getElementById('activityChart').getContext('2d');

      var fillStart = isDarkTheme() ? 'rgba(143, 174, 212, 0.22)' : 'rgba(34, 58, 102, 0.22)';

      var fillEnd = isDarkTheme() ? 'rgba(143, 174, 212, 0.01)' : 'rgba(34, 58, 102, 0.02)';

      charts.push(new Chart(activityCtx, {

        type: 'line',

        data: {

          labels: data.activity.labels,

          datasets: [{

            label: 'Predictions',

            data: data.activity.values,

            borderColor: theme.primary,

            backgroundColor: makeGradient(activityCtx, fillStart, fillEnd),

            fill: true,

            tension: 0.4,

            pointBackgroundColor: theme.accent,

            pointBorderColor: theme.pointBorder,

            pointBorderWidth: 2,

            pointRadius: 5,

            pointHoverRadius: 7,

          }],

        },

        options: {

          responsive: true,

          maintainAspectRatio: false,

          interaction: { mode: 'index', intersect: false },

          plugins: {

            legend: { display: false },

            tooltip: {

              ...sharedTooltip,

              callbacks: {

                label: function (ctx) {

                  return ' ' + ctx.parsed.y + ' prediction' + (ctx.parsed.y === 1 ? '' : 's');

                },

              },

            },

          },

          scales: {

            x: {

              grid: { display: false },

              ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 6, color: theme.muted },

            },

            y: {

              beginAtZero: true,

              ticks: { precision: 0, stepSize: 1, color: theme.muted },

              grid: gridStyle,

            },

          },

        },

      }));

    } else {

      showEmpty('activityChart', true);

    }



    if (data.has_appointments) {

      showEmpty('appointmentChart', false);

      charts.push(new Chart(document.getElementById('appointmentChart'), {

        type: 'doughnut',

        data: {

          labels: data.appointments.labels,

          datasets: [{

            data: data.appointments.values,

            backgroundColor: theme.palette,

            borderWidth: 3,

            borderColor: theme.doughnutBorder,

            hoverOffset: 8,

          }],

        },

        options: {

          responsive: true,

          maintainAspectRatio: false,

          cutout: '62%',

          plugins: {

            legend: {

              position: 'bottom',

              labels: {

                padding: 14,

                usePointStyle: true,

                pointStyle: 'circle',

                color: theme.muted,

                generateLabels: function (chart) {

                  var ds = chart.data.datasets[0];

                  return chart.data.labels.map(function (label, i) {

                    var value = ds.data[i];

                    return {

                      text: label + ' (' + value + ' · ' + percentLabel(value, ds.data) + ')',

                      fillStyle: ds.backgroundColor[i],

                      fontColor: theme.muted,

                      hidden: false,

                      index: i,

                    };

                  });

                },

              },

            },

            tooltip: {

              ...sharedTooltip,

              callbacks: {

                label: function (ctx) {

                  return ' ' + ctx.label + ': ' + ctx.parsed + ' (' + percentLabel(ctx.parsed, ctx.dataset.data) + ')';

                },

              },

            },

          },

        },

      }));

    } else {

      showEmpty('appointmentChart', true);

    }

  }



  buildCharts();

  document.addEventListener('portal-theme-change', buildCharts);
  document.addEventListener('dashboard-theme-change', buildCharts);

})();


