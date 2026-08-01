// Dashboard Chart.js Integration
document.addEventListener('DOMContentLoaded', function() {
  const chartCtx = document.getElementById('consumptionChart');
  if (!chartCtx) return;

  let currentChart = null;

  // Chart dataset definitions
  const chartDatasets = {
    weekly: {
      type: 'bar',
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'Consumption (kWh)',
          data: [12.4, 15.1, 13.8, 14.2, 16.5, 18.2, 18.3],
          backgroundColor: 'rgba(0, 242, 254, 0.6)',
          borderColor: '#00F2FE',
          borderWidth: 2,
          borderRadius: 6
        },
        {
          label: 'Solar Generation (kWh)',
          data: [22.0, 24.5, 20.1, 26.2, 28.0, 21.4, 19.8],
          backgroundColor: 'rgba(0, 255, 157, 0.4)',
          borderColor: '#00FF9D',
          borderWidth: 2,
          borderRadius: 6
        }
      ]
    },
    monthly: {
      type: 'line',
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      datasets: [
        {
          label: 'Consumption (kWh)',
          data: [95.0, 102.5, 110.2, 104.3],
          borderColor: '#00F2FE',
          backgroundColor: 'rgba(0, 242, 254, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 3
        },
        {
          label: 'Solar Generation (kWh)',
          data: [160.0, 175.4, 168.9, 158.2],
          borderColor: '#00FF9D',
          backgroundColor: 'rgba(0, 255, 157, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 3
        }
      ]
    },
    yearly: {
      type: 'line',
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: 'Consumption (kWh)',
          data: [380, 360, 390, 420, 450, 490, 510, 480, 430, 410, 370, 390],
          borderColor: '#FFB800',
          backgroundColor: 'rgba(255, 184, 0, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 3
        },
        {
          label: 'Solar Generation (kWh)',
          data: [420, 450, 520, 580, 640, 680, 660, 610, 540, 490, 430, 410],
          borderColor: '#00FF9D',
          backgroundColor: 'rgba(0, 255, 157, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 3
        }
      ]
    }
  };

  function renderChart(period) {
    if (currentChart) {
      currentChart.destroy();
    }

    const config = chartDatasets[period] || chartDatasets.weekly;

    currentChart = new Chart(chartCtx, {
      type: config.type,
      data: {
        labels: config.labels,
        datasets: config.datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#94A3B8',
              font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' },
              usePointStyle: true,
              padding: 20
            }
          },
          tooltip: {
            backgroundColor: '#0E1626',
            borderColor: '#00F2FE',
            borderWidth: 1,
            titleColor: '#FFF',
            bodyColor: '#94A3B8',
            padding: 12,
            boxPadding: 6
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans' } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans' } }
          }
        }
      }
    });
  }

  // Initial render
  renderChart('weekly');

  // Tab click listeners
  const tabs = document.querySelectorAll('.chart-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const period = this.dataset.period;
      renderChart(period);
    });
  });
});
