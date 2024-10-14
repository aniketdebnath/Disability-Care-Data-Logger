document.addEventListener('DOMContentLoaded', () => {
    let allData = [];
    let filteredData = [];
    let showingFilteredData = false;

    // Fetch initial data from the server
    fetch('/health-data')
        .then(response => response.json())
        .then(data => {
            allData = data;
            updateChartAndTable();
        })
        .catch(error => console.error('Error fetching health data:', error));

    // Create the chart
    const ctx = document.getElementById('healthChart').getContext('2d');
    const healthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Heart Rate',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            }, {
                label: 'Oxygen Saturation',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        tooltipFormat: 'yyyy-MM-dd HH:mm:ss',
                        displayFormats: {
                            minute: 'HH:mm:ss'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    suggestedMin: -10,
                    suggestedMax: 10,
                }
            }
        }
    });

    function updateChartAndTable() {
        const now = new Date();
        const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
        const dataToShow = showingFilteredData ? filteredData : allData.filter(item => new Date(item.DateTime) >= oneHourAgo);

        const labels = dataToShow.map(item => new Date(item.DateTime).toISOString());
        const heartRates = dataToShow.map(item => item.HealthData.HeartRate);
        const oxygenLevels = dataToShow.map(item => item.HealthData.OxygenLevel);

        healthChart.data.labels = labels;
        healthChart.data.datasets[0].data = heartRates.map((value, index) => ({ x: labels[index], y: value }));
        healthChart.data.datasets[1].data = oxygenLevels.map((value, index) => ({ x: labels[index], y: value }));
        healthChart.update();

        const tableBody = document.getElementById('healthDataTableBody');
        tableBody.innerHTML = '';
        dataToShow.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(item.DateTime).toISOString()}</td>
                <td>${item.HealthData.HeartRate}</td>
                <td>${item.HealthData.OxygenLevel}</td>
                <td>${item.HealthData.AccelerometerData.Ax}</td>
                <td>${item.HealthData.AccelerometerData.Ay}</td>
                <td>${item.HealthData.AccelerometerData.Az}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Listen for real-time updates using Socket.io
    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('healthDataUpdate', function(updatedData) {
        console.log('Data received:', updatedData);
        if (updatedData.HealthData) {
            const updatedTime = new Date(updatedData.DateTime);
            allData.push(updatedData);

            if (!showingFilteredData) {
                updateChartAndTable();
            }
        }
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    // Initialize date range picker
    $('#daterange').daterangepicker({
        timePicker: true,
        timePicker24Hour: true,
        startDate: moment().startOf('hour'),
        endDate: moment(),
        locale: {
            format: 'YYYY-MM-DD HH:mm:ss'
        }
    }, function(start, end) {
        const startDate = start.toISOString();
        const endDate = end.toISOString();
        console.log(`New date range selected: ${startDate} to ${endDate}`);

        showingFilteredData = true;
        filteredData = allData.filter(item => new Date(item.DateTime) >= new Date(startDate) && new Date(item.DateTime) <= new Date(endDate));
        updateChartAndTable();
    });

    // Add a button to clear the date filter and show live data
    const clearFilterButton = document.createElement('button');
    clearFilterButton.textContent = 'Show Live Data';
    clearFilterButton.addEventListener('click', () => {
        showingFilteredData = false;
        updateChartAndTable();
    });

    document.querySelector('.daterange-container').appendChild(clearFilterButton);
});
